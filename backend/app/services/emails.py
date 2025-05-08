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
from app.models import Email, EmailCreate, EmailState, Order, OrderCreate, OrderState
from app.repositories.base import CRUDRepository
from app.services.orders import OrderService
from O365 import Account, FileSystemTokenBackend
from sqlmodel import Session

logger = get_logger(__name__)


class EmailService:
    def __init__(
        self,
        session: Session,
        email: str,
    ) -> None:
        self.repository = CRUDRepository[Email](Email, session)
        self.order_service = OrderService(session)
        self.id = settings.OUTLOOK_ID
        self.secret = settings.OUTLOOK_SECRET
        self.email = email

        # Prepare account
        if self.email.endswith("@outlook.com"):
            self.outlook_tenant_id = "consumers"
            self.outlook_scopes = ["Mail.Read", "offline_access"]
        else:
            self.outlook_tenant_id = "common"
            self.outlook_scopes = "https://graph.microsoft.com/Mail.Read offline_access"

        self.token_path = os.path.join(
            os.getcwd(),
            ".gitignores",
            "azure_tokens",
        )
        # logger.info(f"Token path is: {token_path}")
        self.token_backend = FileSystemTokenBackend(
            token_path=self.token_path,
            token_filename=self.email,
        )
        self.account = Account(
            (self.id or "", self.secret or ""),
            token_backend=self.token_backend,
            tenant_id=self.outlook_tenant_id,
        )

    def authenticate(self) -> None:
        if not self.account.is_authenticated:
            logger.info("You need to authenticate with Outlook.")
            url = self.create_outlook_token_step_1()
            logger.info(f"Please visit this URL and authenticate:\n{url}")
            code = input("Paste the code you received here: ").strip()
            success = self.create_outlook_token_step_2(code)
            if not success:
                logger.info("Authentication failed. Exiting.")
                return
            logger.info("Authentication successful!")
        else:
            logger.info("Already authenticated.")

    def create_outlook_token_step_1(self) -> str:
        """
        Step 1: Call this to get the authorization URL. Send this URL to the frontend.
        """
        self.account.connection.scopes = self.outlook_scopes
        url, state = self.account.connection.get_authorization_url()
        logger.info(f"Generated OAuth URL for {self.email}: {url}")
        return url

    def create_outlook_token_step_2(self, code: str) -> bool:
        """
        Step 2: Call this with the code received from the frontend after user authenticates.
        Returns True if authentication succeeded, False otherwise.
        """
        try:
            self.account.connection.request_token(code)
            if self.account.is_authenticated:
                logger.info(f"Authenticated successfully for {self.email}")
                return True
            else:
                logger.error(f"Authentication failed for {self.email}")
                return False
        except Exception as e:
            logger.error(f"Exception during OAuth completion: {e}")
            return False

    async def fetch(self, *, owner_id: uuid.UUID) -> None:
        logger.info(f"Fetching emails for: {self.email}")

        messages = list(
            self.account.mailbox()
            .inbox_folder()
            .get_messages(limit=50, order_by="receivedDateTime desc")
        )
        db_messages = self.get_all(skip=0, limit=100, owner_id=owner_id)

        # Identify new emails
        new_messages = []
        for msg in messages:
            email_id = msg.object_id
            if email_id not in [m.email_id for m in db_messages] or email_id in [
                m.email_id for m in db_messages if not m.state == OrderState.PENDING
            ]:  # Check if email is not on db or was not processed

                # Default state
                state = EmailState.PROCESSED

                # Only process emails with attachments
                if msg.has_attachments:

                    logger.info(f"From: {msg.sender}")
                    for to in msg.to:
                        logger.info(f"To: {to.name} <{to.address}>")
                    logger.info(f"Subject: {msg.subject}")
                    logger.info(f"Received: {msg.received}")
                    logger.info(f"Body: {msg.body_preview}")

                    msg_complete = (
                        self.account.mailbox()
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
                                    state = EmailState.ERROR
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
                self.create(
                    EmailCreate(email_id=email_id, state=state),
                    owner_id=owner_id,
                )
        if not new_messages:
            logger.info(f"No new messages found for {self.email}")

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Email]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def create(self, email_create: EmailCreate, owner_id: uuid.UUID) -> Email:
        return self.repository.create(
            Email.model_validate(email_create, update={"owner_id": owner_id})
        )
