import base64

from app.logger import get_logger
from app.models import Email, User
from O365 import Message

logger = get_logger(__name__)


def _filter_orders(msg_complete: Message, user: User, email: Email) -> list[dict]:

    ##############################################################
    orders = []
    for attachment in msg_complete.attachments:
        if attachment.name.endswith(".pdf"):
            orders.append(
                {
                    "base_document_name": attachment.name,
                    "base_document": base64.b64decode(attachment.content),
                }
            )

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        ##########################################################
        if email.email == "asier.tena.zu@outlook.com":
            if not msg_complete.has_attachments:
                orders.append(
                    {
                        "base_document_name": "email_body.txt",
                        "base_document": msg_complete.body,
                    }
                )

    ##############################################################
    if orders == []:
        logger.warning(f"Non orders found for ID: {msg_complete.object_id}")

    return orders
