from datetime import datetime, timezone

from app.logger import get_logger
from app.models import Order, OrderState, OrderUpdate, User
from pydantic import BaseModel

logger = get_logger(__name__)


def _postprocess_order(order_update: OrderUpdate, user: User) -> OrderUpdate:

    ##############################################################
    order_update.state = OrderState.APPROVED
    is_created_in_erp = False

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        try:
            pass
            # raise NotImplementedError("ERP integration not implemented yet")
            # order_update.state = OrderState.INTEGRATED_OK

        except Exception as e:
            logger.error(f"Error integrating in ERP order: {e}")
            order_update.state = OrderState.INTEGRATED_ERROR

    ##############################################################
    if is_created_in_erp:
        order_update.created_in_erp_at = datetime.now(timezone.utc)

    return order_update
