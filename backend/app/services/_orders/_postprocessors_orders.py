from datetime import datetime, timezone

from app.logger import get_logger
from app.models import Order, OrderState, OrderUpdate, User
from pydantic import BaseModel

logger = get_logger(__name__)


def _postprocess_order(user: User) -> tuple[OrderState, datetime | None]:

    ##############################################################
    state = OrderState.APPROVED

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        try:
            created_in_erp_at = datetime.now(timezone.utc)
            pass
            # raise NotImplementedError("ERP integration not implemented yet")
            # order_update.state = OrderState.INTEGRATED_OK

        except Exception as e:
            logger.error(f"Error integrating in ERP order: {e}")
            state = OrderState.INTEGRATED_ERROR

    return state, created_in_erp_at
