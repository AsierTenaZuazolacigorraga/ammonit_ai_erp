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

logger = get_logger(__name__)


def bridge(func):
    @wraps(func)
    def wrapper(
        ammonit_user: str, ammonit_psw: str, ammonit_base_url: str, *args, **kwargs
    ):
        while True:
            try:

                logger.info("Tying to connect to ammonit api ...")
                time.sleep(10)

                auth_client = AuthenticatedClient(
                    base_url=ammonit_base_url,
                    token=login(
                        client=ApiClient(base_url=ammonit_base_url),
                        body=BodyLoginLoginAccessToken(
                            username=EMAIL, password=PASSWORD
                        ),
                    ).access_token,
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
                                order_state_value = (
                                    order_state.OrderState.INTEGRATED_ERROR
                                )

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

    return wrapper
