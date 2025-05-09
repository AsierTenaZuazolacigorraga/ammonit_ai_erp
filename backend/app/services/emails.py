import base64
import io
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List

from app.core.config import settings
from app.logger import get_logger
from app.models import (
    Email,
    EmailCreate,
    EmailData,
    EmailDataCreate,
    EmailDataState,
    Order,
    OrderCreate,
    OrderState,
)
from app.repositories.base import CRUDRepository
from app.services.orders import OrderService
from app.services.users import UserService
from O365 import Account, FileSystemTokenBackend
from sqlmodel import Session

logger = get_logger(__name__)


class EmailService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.email_repository = CRUDRepository[Email](Email, session)
        self.emaildata_repository = CRUDRepository[EmailData](EmailData, session)
        self.order_service = OrderService(session)
        self.user_service = UserService(session)
        self.id = settings.OUTLOOK_ID
        self.secret = settings.OUTLOOK_SECRET
        self.accounts = {}

    def authenticate(self, email: str) -> None:
        if not self.accounts[email]["account"].is_authenticated:
            logger.info("You need to authenticate with Outlook.")
            url = self.create_outlook_token_step_1(email)
            logger.info(f"Please visit this URL and authenticate:\n{url}")
            code = input("Paste the code you received here: ").strip()
            success = self.create_outlook_token_step_2(email, code)
            if not success:
                logger.info("Authentication failed. Exiting.")
                return
            logger.info("Authentication successful!")
        else:
            logger.info("Already authenticated.")

    def create_outlook_token_step_1(self, email: str) -> str:
        """
        Step 1: Call this to get the authorization URL. Send this URL to the frontend.
        """
        if email not in self.accounts:
            raise ValueError(f"Email {email} not found in accounts")
        self.accounts[email]["account"].connection.scopes = self.accounts[email][
            "outlook_scopes"
        ]
        url, state = self.accounts[email]["account"].connection.get_authorization_url()
        logger.info(f"Generated OAuth URL for {email}: {url}")
        return url

    def create_outlook_token_step_2(self, email: str, code: str) -> bool:
        """
        Step 2: Call this with the code received from the frontend after user authenticates.
        Returns True if authentication succeeded, False otherwise.
        """
        if email not in self.accounts:
            raise ValueError(f"Email {email} not found in accounts")
        try:
            self.accounts[email]["account"].connection.request_token(code)
            if self.accounts[email]["account"].is_authenticated:
                logger.info(f"Authenticated successfully for {email}")
                return True
            else:
                logger.error(f"Authentication failed for {email}")
                return False
        except Exception as e:
            logger.error(f"Exception during OAuth completion: {e}")
            return False

    def load_all(self, owner_id: uuid.UUID) -> None:

        # Get all emails
        emails = self.get_all(skip=0, limit=50, owner_id=owner_id)

        # Load info and update accounts
        for email in emails:
            self.load(email.email)

    def load_by_id(self, id: uuid.UUID) -> None:

        # Get email
        email = self.email_repository.get_by_id(id)
        if not email:
            return None
        self.load(email.email)

    def load(self, email: str) -> None:

        # Prepare account
        if email.endswith("@outlook.com"):
            self.accounts[email] = {
                "outlook_tenant_id": "consumers",
                "outlook_scopes": ["Mail.Read", "offline_access"],
            }
        else:
            self.accounts[email] = {
                "outlook_tenant_id": "common",
                "outlook_scopes": "https://graph.microsoft.com/Mail.Read offline_access",
            }
        token_path = os.path.join(
            os.getcwd(),
            ".gitignores",
            "azure_tokens",
        )
        self.accounts[email]["token_backend"] = FileSystemTokenBackend(
            token_path=token_path,
            token_filename=email,
        )
        self.accounts[email]["account"] = Account(
            (self.id or "", self.secret or ""),
            token_backend=self.accounts[email]["token_backend"],
            tenant_id=self.accounts[email]["outlook_tenant_id"],
        )

    def email_create(self, email_create: EmailCreate, owner_id: uuid.UUID) -> Email:
        return self.email_repository.create(
            Email.model_validate(
                email_create, update={"owner_id": owner_id, "is_connected": False}
            )
        )

    def emaildata_create(
        self, email_data_create: EmailDataCreate, owner_id: uuid.UUID
    ) -> EmailData:
        return self.emaildata_repository.create(
            EmailData.model_validate(email_data_create, update={"owner_id": owner_id})
        )

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Email]:
        return self.email_repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Email | None:
        return self.email_repository.get_by_id(id)

    def get_by_email(self, email: str) -> Email | None:
        emails = self.email_repository.get_all_by_kwargs(email=email)
        if len(emails) > 1:
            raise ValueError(f"Multiple emails found with email {email}")
        return emails[0] if emails else None

    def get_count(self, owner_id: uuid.UUID) -> int:
        return self.email_repository.count_by_kwargs(**{"owner_id": owner_id})

    async def fetch(self, *, owner_id: uuid.UUID) -> None:

        # Fetch emails
        for k, v in self.accounts.items():

            email = self.get_by_email(email=k)
            if not email:
                logger.warning(f"Email {k} not found")
                continue

            account = v["account"]

            logger.info(f"Fetching emails for: {email.email}")

            messages = list(
                account.mailbox()
                .inbox_folder()
                .get_messages(limit=50, order_by="receivedDateTime desc")
            )
            db_messages = self.emaildata_repository.get_all_by_kwargs(
                owner_id=email.id,
                state=EmailDataState.PROCESSED,
            )

            # Identify new emails
            new_messages = []
            for msg in messages:
                if msg.object_id not in [
                    m.email_id for m in db_messages
                ] or msg.object_id in [
                    m.email_id for m in db_messages if not m.state == OrderState.PENDING
                ]:  # Check if email is not on db or was not processed

                    # Default state
                    state = EmailDataState.PROCESSED

                    # Only process emails with attachments
                    from app.services._emails.filters import filters

                    if filters(msg, self.user_service.get_by_id(owner_id), email):

                        logger.info(f"From: {msg.sender}")
                        for to in msg.to:
                            logger.info(f"To: {to.name} <{to.address}>")
                        logger.info(f"Subject: {msg.subject}")
                        logger.info(f"Received: {msg.received}")
                        logger.info(f"Body: {msg.body_preview}")

                        msg_complete = (
                            account.mailbox()
                            .inbox_folder()
                            .get_message(msg.object_id, download_attachments=True)
                        )
                        if msg_complete:

                            for attachment in msg_complete.attachments:
                                if attachment.name.endswith(".pdf"):

                                    base_document_name = attachment.name
                                    base_document = base64.b64decode(attachment.content)

                                    try:
                                        # Create the order
                                        await self.order_service.create(
                                            order_create=OrderCreate(
                                                base_document=base_document or None,
                                                base_document_name=base_document_name
                                                or None,
                                            ),
                                            owner_id=owner_id,
                                        )
                                    except Exception as e:
                                        state = EmailDataState.ERROR
                                        logger.error(f"Failed to create order: {e}")
                                else:
                                    logger.warning(
                                        f"Non .pdf attachment found for ID: {msg.object_id}"
                                    )
                        else:
                            logger.warning(
                                f"Failed to retrieve message for ID: {msg.object_id}"
                            )
                    else:
                        logger.warning(f"No attachments found for ID: {msg.object_id}")

                    # Save it for tracing
                    new_messages.append(msg)
                    self.emaildata_create(
                        email_data_create=EmailDataCreate(
                            email_id=msg.object_id,
                            email_body=msg.body_preview,
                            state=state,
                        ),
                        owner_id=email.id,
                    )
            if not new_messages:
                logger.info(f"No new messages found for {email.email}")
