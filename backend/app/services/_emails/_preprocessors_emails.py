import base64

from app.logger import get_logger
from app.models import Email, OfferCreate, OrderCreate, User
from O365 import Message

logger = get_logger(__name__)


def _preprocessors_emails_orders(
    msg_complete: Message, user: User, email: Email
) -> list[OrderCreate]:

    ##############################################################
    orders = []
    for attachment in msg_complete.attachments:
        if attachment.name.endswith(".pdf"):
            orders.append(
                OrderCreate(
                    base_document_name=attachment.name,
                    base_document=base64.b64decode(attachment.content),
                )
            )

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        ##########################################################
        if email.email == "asier.tena.zu@outlook.com":
            pass

    ##############################################################
    if orders == []:
        logger.warning(f"Non orders found for ID: {msg_complete.object_id}")

    return orders


def _preprocessors_emails_offers(
    msg_complete: Message, user: User, email: Email
) -> list[OfferCreate]:

    ##############################################################
    offers = [
        OfferCreate(
            base_message="""
Me gustaría comprar estas referencias:
1540307080232 - ARANDELA ARRASTRE ALLEN -> 10 pcs
1551010015006 - Casquillo separador 100x115x6 -> 10 pcs
""",
        )
    ]

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        ##########################################################
        if email.email == "asier.tena.zu@outlook.com":
            pass

    ##############################################################
    if offers == []:
        logger.warning(f"Non offers found for ID: {msg_complete.object_id}")

    return offers
