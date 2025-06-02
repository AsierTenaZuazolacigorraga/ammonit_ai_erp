import getpass
import os
import time
import traceback
from datetime import datetime, timezone
from functools import wraps

from app.api_client.ammonit_client import AuthenticatedClient
from app.api_client.ammonit_client import Client as ApiClient
from app.api_client.ammonit_client.api.login.login_login_access_token import (
    sync as login,
)
from app.api_client.ammonit_client.api.orders.orders_read_orders import (
    sync as read_orders,
)
from app.api_client.ammonit_client.api.orders.orders_update_order_erp_state import (
    sync as update_order_erp_state,
)
from app.api_client.ammonit_client.models import order_state
from app.api_client.ammonit_client.models.body_login_login_access_token import (
    BodyLoginLoginAccessToken,
)
from app.api_client.ammonit_client.models.order_update import OrderUpdate
from app.logger import get_logger
from dotenv import load_dotenv

logger = get_logger(__name__)


def bridge(func, *args, **kwargs):

    if func is None:
        raise ValueError("A function must be provided as an argument")
    while True:
        try:

            logger.info("Tying to connect to ammonit api ...")
            time.sleep(10)

            # Get arguments
            load_dotenv(override=True)
            ammonit_base_url = os.getenv("BASE_URL")
            if ammonit_base_url is None:
                raise ValueError("AMMONIT_BASE_URL is not set")
            ammonit_user = os.getenv("EMAIL")
            if ammonit_user is None:
                raise ValueError("AMMONIT_USER is not set")
            ammonit_psw = os.getenv("PASSWORD")
            if ammonit_psw is None:
                raise ValueError("AMMONIT_PSW is not set")

            # Login
            auth_login = login(
                client=ApiClient(base_url=ammonit_base_url),
                body=BodyLoginLoginAccessToken(
                    username=ammonit_user, password=ammonit_psw
                ),
            )
            if auth_login is None:
                raise ValueError("Failed to login, check credentials")
            auth_client = AuthenticatedClient(
                base_url=ammonit_base_url,
                token=auth_login.access_token,
            )

            while True:

                logger.info("Processing orders ...")
                time.sleep(10)

                orders = read_orders(client=auth_client)
                if orders:
                    orders = [
                        order
                        for order in orders.data
                        if order.state == order_state.OrderState.APPROVED
                    ]
                    for order in orders:

                        logger.info(f"Processing order: {order.id}")
                        try:
                            order_state_value = func(*args, **kwargs)
                        except Exception as e:
                            logger.error(f"Error processing order: {e}")
                            order_state_value = order_state.OrderState.INTEGRATED_ERROR

                        # Update the order
                        update_order_erp_state(
                            client=auth_client,
                            body=OrderUpdate(
                                state=order_state_value,
                                created_in_erp_at=datetime.now(timezone.utc),
                            ),
                            id=order.id,
                        )

        except Exception as e:
            logger.error(
                "Error in task %s: %s\nTraceback:\n%s",
                func.__name__,
                str(e),
                traceback.format_exc(),
            )
