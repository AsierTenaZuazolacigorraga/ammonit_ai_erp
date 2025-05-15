import getpass
import os
import time

from app.api_client.ammonit_client import AuthenticatedClient
from app.api_client.ammonit_client import Client as ApiClient
from app.api_client.ammonit_client.api.login.login_login_access_token import (
    sync as login,
)
from app.api_client.ammonit_client.api.orders.orders_read_orders import (
    sync as read_orders,
)
from app.api_client.ammonit_client.models.body_login_login_access_token import (
    BodyLoginLoginAccessToken,
)
from app.logger import get_logger

logger = get_logger(__name__)

PASSWORD = getpass.getpass()
EMAIL = "asier.tena.zu@outlook.com"


def main():

    while True:
        try:

            logger.info("Tying to connect to ammonit api ...")
            time.sleep(1)

            client = AuthenticatedClient(
                base_url=os.getenv("FASTAPI_HOST_PROD") or "",
                token=login(
                    client=ApiClient(base_url=os.getenv("FASTAPI_HOST_PROD") or ""),
                    body=BodyLoginLoginAccessToken(username=EMAIL, password=PASSWORD),
                ).access_token,
            )

            while True:

                logger.info("Processing orders ...")
                time.sleep(1)

                orders = read_orders(client=client)
                logger.info(f"Orders: {orders}")

        except KeyboardInterrupt:
            logger.info("Bridge stopped")


if __name__ == "__main__":
    main()
