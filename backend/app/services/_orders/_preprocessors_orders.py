from app.logger import get_logger
from app.models import Order, User
from pydantic import BaseModel

logger = get_logger(__name__)


def _preprocess_order(order_basemodel: BaseModel, user: User) -> dict:

    ##############################################################
    order_dict = order_basemodel.model_dump()
    for item in order_dict["items"]:
        item["our_code"] = ""

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        # Populate order with ERP data firts, before creating it
        for item in order_dict["items"]:
            item["our_code"] = "TBD"

    return order_dict
