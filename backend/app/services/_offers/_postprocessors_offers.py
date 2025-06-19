from datetime import datetime, timezone

from app.logger import get_logger
from app.models import Offer, OfferState, OfferUpdate, User

logger = get_logger(__name__)


def _postprocess_offer(user: User) -> OfferState:

    ##############################################################
    state = OfferState.APPROVED

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        try:
            pass
            # raise NotImplementedError("ERP integration not implemented yet")
            # order_update.state = OrderState.INTEGRATED_OK

        except Exception as e:
            logger.error(f"Error integrating in ERP order: {e}")
            state = OfferState.INTEGRATED_ERROR

    return state
