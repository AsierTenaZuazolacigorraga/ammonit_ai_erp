import json
import os
from datetime import datetime, timezone

from app.core.config import settings
from app.core.db import engine
from app.logger import get_logger
from app.models import Client, ClientCreate
from app.services.clients import ClientService
from app.services.users import UserService
from sqlmodel import Session

logger = get_logger(__name__)


def main():
    with Session(engine) as session:
        user_service = UserService(session)
        for user in user_service.repository.get_all():

            # Only process desired user
            if user.full_name == "Asier":

                # Define clients service
                client_service = ClientService(session)

                # Create a test client
                client = client_service.create(
                    ClientCreate(
                        name="ulma",
                        clasifier="Contiene la palabra y referencias a la empresa de Ulma",
                        structure=json.dumps(
                            {
                                "format": {
                                    "type": "json_schema",
                                    "name": "order_ulma",
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "number": {
                                                "type": "string",
                                                "description": "The number of the order. Usually provided in a table called 'Pedido de compra', in the field names as 'Num.'.",
                                            },
                                            "items": {
                                                "type": "array",
                                                "description": "The items in the order",
                                                "items": {"$ref": "#/$defs/item_ulma"},
                                            },
                                        },
                                        "required": ["number", "items"],
                                        "additionalProperties": False,
                                        "$defs": {
                                            "item_ulma": {
                                                "type": "object",
                                                "description": "Defines an item in the order.",
                                                "properties": {
                                                    "code": {
                                                        "type": "string",
                                                        "description": "The code of the item. Usually provided as 'Proyecto Código'.",
                                                    },
                                                    "description": {
                                                        "type": "string",
                                                        "description": "The description of the item.",
                                                    },
                                                    "quantity": {
                                                        "type": "number",
                                                        "description": "The quantity of items to order",
                                                    },
                                                    "unit_price": {
                                                        "type": "number",
                                                        "description": "The unit price of the item. Usually provided as 'Precio'.",
                                                    },
                                                    "deadline": {
                                                        "type": "string",
                                                        "description": "The deadline or due date for the item. Usually provided as 'Entrega'.",
                                                    },
                                                },
                                                "required": [
                                                    "code",
                                                    "description",
                                                    "quantity",
                                                    "unit_price",
                                                    "deadline",
                                                ],
                                                "additionalProperties": False,
                                            }
                                        },
                                    },
                                    "strict": True,
                                }
                            },
                        ),
                    ),
                    owner_id=user.id,
                )
                logger.info(
                    f"Created client: {client.name} with structure: {client.structure}"
                )


if __name__ == "__main__":
    main()
