import getpass
import os
import time
from app.bridge.bridge import bridge
from app.logger import get_logger

logger = get_logger(__name__)

BASE_URL = os.getenv("FASTAPI_HOST")
# BASE_URL = os.getenv("FASTAPI_HOST_PROD")
EMAIL = os.getenv("FIRST_SUPERUSER")
PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD")


@bridge
def bridge_instance(*args, **kwargs) -> order_state.OrderState:

    import random

    random_number = random.randint(1, 10)
    if random_number > 5:
        order_state_value = order_state.OrderState.INTEGRATED_OK
    else:
        order_state_value = order_state.OrderState.INTEGRATED_ERROR
    return order_state_value


def main():

    bridge_instance(EMAIL, PASSWORD, BASE_URL)


if __name__ == "__main__":
    main()
