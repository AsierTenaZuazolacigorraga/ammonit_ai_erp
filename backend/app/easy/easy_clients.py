import getpass
import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Union

from app.api_client.ammonit_client import AuthenticatedClient
from app.api_client.ammonit_client import Client as ApiClient
from app.api_client.ammonit_client.api.clients.clients_create_client import (
    sync as create_client,
)
from app.api_client.ammonit_client.api.login.login_login_access_token import (
    sync as login,
)
from app.api_client.ammonit_client.api.orders.orders_read_orders import (
    sync as read_orders,
)
from app.api_client.ammonit_client.models.body_login_login_access_token import (
    BodyLoginLoginAccessToken,
)
from app.api_client.ammonit_client.models.client_create import (
    ClientCreate as ClientCreateApi,
)
from app.core.db import engine
from app.logger import get_logger
from app.services.clients import ClientCreate, ClientService
from app.services.users import UserService
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sqlmodel import Session

logger = get_logger(__name__)


load_dotenv()


# Classes
class Item(BaseModel):
    code: str = Field(
        ...,
        description=f"The number of the order",
    )
    description: str = Field(
        ...,
        description=f"The description of the item",
    )
    quantity: int = Field(
        ...,
        description=f"The quantity of items to order",
    )
    unit_price: float = Field(..., description=f"The unit price of the item")
    deadline: str = Field(
        ...,
        description=f"The deadline or due date for the item",
    )


class Order(BaseModel):
    number: str = Field(
        ...,
        description=f"The number of the order",
    )
    items: List[Item] = Field(
        ...,
        description=f"The items in the order",
    )


def adapt_schema(schema: dict) -> dict:
    schema.update({"additionalProperties": False})
    schema.pop("title")
    return schema


# Parameters
IS_LOCAL = False
EMAIL = "asier.tena.zu@outlook.com"
CLIENT_NAME = "nearby"
CLIENT_CLASSIFIER = (
    "Contiene la palabra y referencias a la empresa de Nearby Electronics"
)
CLIENT_STRUCTURE = Order.model_json_schema()
CLIENT_STRUCTURE = adapt_schema(CLIENT_STRUCTURE)
for defs in CLIENT_STRUCTURE["$defs"]:
    CLIENT_STRUCTURE["$defs"][defs] = adapt_schema(CLIENT_STRUCTURE["$defs"][defs])
CLIENT_STRUCTURE = {
    "format": {
        "type": "json_schema",
        "name": "order",
        "strict": True,
        "schema": CLIENT_STRUCTURE,
    }
}


def main():
    if IS_LOCAL:
        logger.info("Running locally")
        with Session(engine) as session:
            user_service = UserService(session)
            for user in user_service.repository.get_all():

                # Only process desired user
                if user.email == EMAIL:

                    # Define clients service
                    client_service = ClientService(session)

                    # Create a test client
                    client = client_service.create(
                        ClientCreate(
                            name=CLIENT_NAME,
                            clasifier=CLIENT_CLASSIFIER,
                            structure=json.dumps(CLIENT_STRUCTURE),
                        ),
                        owner_id=user.id,
                    )
                    logger.info(
                        f"Created client: {client.name} with structure: {client.structure}"
                    )
    else:
        logger.info("Running in cloud")

        # Login
        password = getpass.getpass("Please enter your password: ")
        client = AuthenticatedClient(
            base_url=os.getenv("FASTAPI_HOST_PROD") or "",
            token=login(
                client=ApiClient(base_url=os.getenv("FASTAPI_HOST_PROD") or ""),
                body=BodyLoginLoginAccessToken(username=EMAIL, password=password),
            ).access_token,
        )
        create_client(
            client=client,
            body=ClientCreateApi(
                name=CLIENT_NAME,
                clasifier=CLIENT_CLASSIFIER,
                structure=json.dumps(CLIENT_STRUCTURE),
            ),
        )


if __name__ == "__main__":
    main()
