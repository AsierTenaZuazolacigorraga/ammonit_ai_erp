from app.logger import get_logger
from app.models import Order, User

logger = get_logger(__name__)


def _process_dict_fields(order_columns_mapping: dict, old_dict: dict) -> dict:

    new_dict = {}

    for field, value in old_dict.items():
        # If value is a dictionary, process it recursively
        if isinstance(value, dict):
            new_dict[field] = _process_dict_fields(order_columns_mapping, value)
        # If value is a list of dictionaries, process each item
        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            new_dict[field] = [
                _process_dict_fields(order_columns_mapping, item) for item in value
            ]
        # If field exists in mapping
        elif field in order_columns_mapping:
            # If field should be included, rename it according to mapping
            if order_columns_mapping[field]["include"]:
                new_dict[order_columns_mapping[field]["column"]] = value
        # If field is not in mapping, keep it as is
        else:
            new_dict[field] = value

    if isinstance(new_dict, dict) and "items" in new_dict:
        for idx, item in enumerate(new_dict["items"]):
            item_keys = list(item.keys())
            item_keys.insert(1, "Código Item Propio")
            # Create a new dict with the desired key order
            new_item = {k: (item[k] if k in item else "") for k in item_keys}
            new_dict["items"][idx] = new_item

    return new_dict


def _preprocess_order(
    order_columns_mapping: dict, order_dict: dict, user: User
) -> dict:

    ##############################################################
    order_dict = _process_dict_fields(order_columns_mapping, order_dict)

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":
        # Populate order with ERP data firts, before creating it
        for item in order_dict["items"]:
            item["Código Item Propio"] = "TBD"

    return order_dict
