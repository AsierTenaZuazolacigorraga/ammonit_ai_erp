import getpass
import os
import time

from app.api_client.ammonit_client.models import order_state
from app.logger import get_logger
from dotenv import load_dotenv

from backend.bridge.bridge import bridge

load_dotenv()

logger = get_logger(__name__)


def bridge_instance(*args, **kwargs) -> order_state.OrderState:

    import random

    random_number = random.randint(1, 10)
    if random_number > 5:
        order_state_value = order_state.OrderState.INTEGRATED_OK
    else:
        order_state_value = order_state.OrderState.INTEGRATED_ERROR
    return order_state_value


bridge(bridge_instance)
