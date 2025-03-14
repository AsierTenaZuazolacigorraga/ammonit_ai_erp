import base64
import io
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List

from app.logger import get_logger
from O365 import Account, FileSystemTokenBackend

logger = get_logger(__name__)

################################################################

OUTLOOK_ID = "x"
OUTLOOK_SECRET = "x"

OUTLOOK_EMAIL = "asier.tena.zu@outlook.com"
OUTLOOK_SCOPES = "Mail.Read,offline_access"

################################################################
token_path = os.path.join(
    os.getcwd(),
    ".gitignores",
    "azure_tokens",
)
logger.info(f"Token path is: {token_path}")
token_backend = FileSystemTokenBackend(
    token_path=token_path,
    token_filename=OUTLOOK_EMAIL,
)
account = Account(
    (OUTLOOK_ID, OUTLOOK_SECRET),
    token_backend=token_backend,
    tenant_id="consumers",
)
if account.is_authenticated:
    logger.info("Token loaded successfully.")
else:
    if account.authenticate(
        scopes=OUTLOOK_SCOPES if isinstance(OUTLOOK_SCOPES, list) else [OUTLOOK_SCOPES]
    ):
        logger.info("Authenticated successfully")
    else:
        raise Exception("Authentication failed")

messages = list(
    account.mailbox()
    .inbox_folder()
    .get_messages(limit=50, order_by="receivedDateTime desc")
)

if messages:
    first_message = messages[0]
    print(f"Email read:\n\n")
    print(f"Subject: {first_message.subject}")
    print(f"Sender: {first_message.sender}")
    print(f"Date: {first_message.created}")
    print(f"Content: {first_message.body}")
else:
    print("No messages found.")
