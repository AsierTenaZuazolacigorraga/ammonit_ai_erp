from datetime import datetime, timezone

from app.logger import get_logger
from app.models import Order, OrderState, OrderUpdate, User
from pydantic import BaseModel

logger = get_logger(__name__)


def _postprocess_order(order_update: OrderUpdate, user: User) -> OrderUpdate:

    ##############################################################
    try:
        order_update.state = OrderState.INTEGRATED

        ##########################################################
        if user.email == "asier.tena.zu@outlook.com":

            raise NotImplementedError("ERP integration not implemented yet")

    except Exception as e:
        logger.error(f"Error integrating in ERP order: {e}")
        order_update.state = OrderState.ERROR

    ##############################################################
    order_update.created_in_erp_at = datetime.now(timezone.utc)

    return order_update
