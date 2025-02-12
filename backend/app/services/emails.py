import base64
import io
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List

from app.app_logging import get_logger
from app.models import Email, EmailCreate, Order, OrderCreate
from app.repositories.emails import EmailRepository
from app.services.orders import OrderService
from O365 import Account, FileSystemTokenBackend

logger = get_logger()


class EmailService:
    def __init__(
        self,
        repository: EmailRepository,
        order_service: OrderService,
        id: str | None,
        secret: str | None,
        email: str,
        scopes: List[str] | str,
    ) -> None:
        self.repository = repository
        self.order_service = order_service
        self.id = id
        self.secret = secret
        self.email = email
        self.scopes = scopes
        self.token_backend = FileSystemTokenBackend(
            token_path=os.path.join(
                os.getcwd(),
                "..",
                ".gitignores",
                "azure_tokens",
            ),
            token_filename=self.email,
        )
        self.account = Account(
            (self.id or "", self.secret or ""),
            token_backend=self.token_backend,
            tenant_id="consumers",
        )
        if self.account.is_authenticated:
            pass
            # logger.info("Token loaded successfully.")
        else:
            if self.account.authenticate(
                scopes=self.scopes if isinstance(self.scopes, list) else [self.scopes]
            ):
                pass
                # logger.info("Authenticated successfully")
            else:
                logger.info("Authentication failed")

    def fetch(self, *, owner_id: uuid.UUID) -> None:

        messages = list(
            self.account.mailbox()
            .inbox_folder()
            .get_messages(limit=50, order_by="receivedDateTime asc")
        )
        new_messages = []
        db_messages = self.repository.get_all()

        # Identify new emails
        for msg in messages:
            email_id = msg.object_id
            if email_id not in [m.email_id for m in db_messages] or email_id in [
                m.email_id for m in db_messages if not m.is_processed
            ]:  # Check if email is not on db or was not processed

                # By now, only allow valid emails for order creation:
                # - Emails sent from atena@caf.net
                # - Emails with attachment
                # - Emails with only 1 attachment
                if msg.has_attachments and msg.sender.address == "atena@caf.net":

                    logger.info(f"From: {msg.sender}")
                    logger.info(f"Subject: {msg.subject}")
                    logger.info(f"Received: {msg.received}")
                    logger.info(f"Body: {msg.body_preview}")

                    msg = (
                        self.account.mailbox()
                        .inbox_folder()
                        .get_message(msg.object_id, download_attachments=True)
                    )
                    in_document_name = msg.attachments[0].name
                    in_document = base64.b64decode(msg.attachments[0].content)

                    # Create the order
                    self.order_service.create(
                        order_create=OrderCreate(
                            date_local=datetime.now(),
                            date_utc=datetime.now(timezone.utc),
                            in_document=in_document or None,
                            in_document_name=in_document_name or None,
                        ),
                        owner_id=owner_id,
                    )

                # Save it for tracing
                new_messages.append(msg)
                self.repository.create(
                    Email.model_validate(
                        EmailCreate(email_id=email_id, is_processed=True),
                        update={"owner_id": owner_id},
                    )
                )
