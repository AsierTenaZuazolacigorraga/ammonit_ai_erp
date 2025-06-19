from app.logger import get_logger
from app.models import Order, User

logger = get_logger(__name__)


def _preprocess_offer(
    offer_columns_mapping: dict, offer_dict: dict, user: User
) -> dict:

    # ##############################################################
    # offer_dict = _process_dict_fields(offer_columns_mapping, offer_dict)

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":
        # Populate order with ERP data firts, before creating it
        for item in offer_dict["items"]:
            item["Código Item Propio"] = "TBD"

    return offer_dict
