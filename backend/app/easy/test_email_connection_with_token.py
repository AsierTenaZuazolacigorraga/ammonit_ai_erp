import base64
import io
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List

from app.logger import get_logger
from dotenv import load_dotenv
from O365 import Account, FileSystemTokenBackend

logger = get_logger(__name__)

################################################################

load_dotenv()

OUTLOOK_ID = os.getenv("OUTLOOK_ID")
OUTLOOK_SECRET = os.getenv("OUTLOOK_SECRET")

OUTLOOK_EMAIL = "alberdi.autom@outlook.com"
OUTLOOK_SCOPES = "Mail.Read,offline_access"

################################################################
token_path = os.path.join(
    os.getcwd(),
    "backend",
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
    for message in messages[:5]:  # Limit to the first 5 messages
        print(f"Email read:\n\n")
        print(f"Subject: {message.subject}")
        print(f"Sender: {message.sender}")
        print(f"Date: {message.created}")
        print(f"Content: {message.body}")
else:
    print("No messages found.")
