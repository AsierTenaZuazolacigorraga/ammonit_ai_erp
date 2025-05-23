from app.logger import get_logger
from app.models import Order, User

logger = get_logger(__name__)


def _preprocess_order(order_dict: dict, user: User) -> dict:

    ##############################################################
    for idx, item in enumerate(order_dict["items"]):
        item_keys = list(item.keys())
        item_keys.insert(1, "Código Item Propio")
        # Create a new dict with the desired key order
        new_item = {k: (item[k] if k in item else "") for k in item_keys}
        order_dict["items"][idx] = new_item

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        # Populate order with ERP data firts, before creating it
        for item in order_dict["items"]:
            item["Código Item Propio"] = "1234"

    return order_dict
