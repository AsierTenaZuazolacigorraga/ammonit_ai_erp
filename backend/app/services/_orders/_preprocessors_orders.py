from app.logger import get_logger
from app.models import Order, User

logger = get_logger(__name__)


def _preprocess_order(order_dict: dict, user: User) -> dict:

    ##############################################################
    for item in order_dict["items"]:
        item["our_code"] = ""

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        # Populate order with ERP data firts, before creating it
        for item in order_dict["items"]:
            item["our_code"] = "1234"

    return order_dict
