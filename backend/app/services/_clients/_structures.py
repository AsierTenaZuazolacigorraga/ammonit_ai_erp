from typing import List

from app.models import Client, User
from pydantic import BaseModel, Field


def _get_client_structure(user: User, client: Client) -> type[BaseModel]:

    ##############################################################
    GENERIC_NUMBER_DESC = "The number of the order"
    GENERIC_ITEMS_DESC = "The items in the order"
    GENERIC_CODE_DESC = "The code of the item"
    GENERIC_DESCRIPTION_DESC = "The description of the item"
    GENERIC_QUANTITY_DESC = "The quantity of items to order"
    GENERIC_UNIT_PRICE_DESC = "The unit price of the item"
    GENERIC_DEADLINE_DESC = "The deadline or due date for the item"

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        ##########################################################
        if client.name == "danobat":

            class Item(BaseModel):
                client_code: str = Field(
                    ...,
                    description=f"{GENERIC_CODE_DESC}",
                )
                description: str = Field(
                    ...,
                    description=f"{GENERIC_DESCRIPTION_DESC}",
                )
                quantity: int = Field(
                    ...,
                    description=f"{GENERIC_QUANTITY_DESC}",
                )
                unit_price: float = Field(..., description=f"{GENERIC_UNIT_PRICE_DESC}")
                deadline: str = Field(
                    ...,
                    description=f"{GENERIC_DEADLINE_DESC}",
                )

            class Order(BaseModel):
                number: str = Field(
                    ...,
                    description=f"{GENERIC_NUMBER_DESC}",
                )
                items: List[Item] = Field(
                    ...,
                    description=f"{GENERIC_ITEMS_DESC}",
                )

            return Order

        ##########################################################
        elif client.name == "fagor":

            class Item(BaseModel):
                client_code: str = Field(
                    ...,
                    description=f"{GENERIC_CODE_DESC}. The code is usually repeated two times.",
                )
                description: str = Field(
                    ...,
                    description=f"{GENERIC_DESCRIPTION_DESC}",
                )
                quantity: int = Field(
                    ...,
                    description=f"{GENERIC_QUANTITY_DESC}",
                )
                unit_price: float = Field(
                    ...,
                    description=f"{GENERIC_UNIT_PRICE_DESC}. Be careful, report only the unit price (sometimes are provided both the unit price and the total price).",
                )
                deadline: str = Field(
                    ...,
                    description=f"{GENERIC_DEADLINE_DESC}",
                )

            class Order(BaseModel):
                number: str = Field(
                    ...,
                    description=f"{GENERIC_NUMBER_DESC}. Usually is provided as 'Eskari'.",
                )
                items: List[Item] = Field(
                    ...,
                    description=f"{GENERIC_ITEMS_DESC}",
                )

            return Order

        ##########################################################
        elif client.name == "inola":

            class Item(BaseModel):
                client_code: str = Field(..., description=f"{GENERIC_CODE_DESC}")
                description: str = Field(..., description=f"{GENERIC_DESCRIPTION_DESC}")
                quantity: int = Field(..., description=f"{GENERIC_QUANTITY_DESC}")
                unit_price: float = Field(..., description=f"{GENERIC_UNIT_PRICE_DESC}")
                deadline: str = Field(
                    ...,
                    description=f"{GENERIC_DEADLINE_DESC}. Usually the deadline is provided for the entire order (as F.ENTREGA) rather than for each item independently",
                )

            class Order(BaseModel):
                number: str = Field(..., description=f"{GENERIC_NUMBER_DESC}")
                items: List[Item] = Field(..., description=f"{GENERIC_ITEMS_DESC}")

            return Order

        ##########################################################
        elif client.name == "matisa":

            class Item(BaseModel):
                client_code: str = Field(
                    ...,
                    description=f"{GENERIC_CODE_DESC}. Usually provided as 'Référence article et désignation'. The code is provided in digits in this format: XX-XX-XXX-XXXXX.",
                )
                description: str = Field(
                    ...,
                    description=f"{GENERIC_DESCRIPTION_DESC}. Usually provided as 'Référence article et désignation'. Consider description all but the code.",
                )
                quantity: int = Field(..., description=f"{GENERIC_QUANTITY_DESC}")
                unit_price: float = Field(..., description=f"{GENERIC_UNIT_PRICE_DESC}")
                deadline: str = Field(..., description=f"{GENERIC_DEADLINE_DESC}")

            class Order(BaseModel):
                number: str = Field(
                    ...,
                    description=f"{GENERIC_NUMBER_DESC}. Usually provided as 'COMMANDE ACHAT'.",
                )
                items: List[Item] = Field(..., description=f"{GENERIC_ITEMS_DESC}")

            return Order

        ##########################################################
        elif client.name == "ulma":

            class Item(BaseModel):
                client_code: str = Field(
                    ...,
                    description=f"{GENERIC_CODE_DESC}. Usually provided as 'Proyecto Código'.",
                )
                description: str = Field(..., description=f"{GENERIC_DESCRIPTION_DESC}")
                quantity: int = Field(..., description=f"{GENERIC_QUANTITY_DESC}")
                unit_price: float = Field(
                    ...,
                    description=f"{GENERIC_UNIT_PRICE_DESC}. Usually provided as 'Precio'.",
                )
                deadline: str = Field(
                    ...,
                    description=f"{GENERIC_DEADLINE_DESC}. Usually provided as 'Entrega'.",
                )

            class Order(BaseModel):
                number: str = Field(
                    ...,
                    description=f"{GENERIC_NUMBER_DESC}. Usually provided in a table called 'Pedido de compra', in the field names as 'Num.'.",
                )
                items: List[Item] = Field(..., description=f"{GENERIC_ITEMS_DESC}")

            return Order

        ##########################################################
        elif client.name == "nearby":

            class Item(BaseModel):
                client_code: str = Field(..., description=f"{GENERIC_CODE_DESC}")
                description: str = Field(..., description=f"{GENERIC_DESCRIPTION_DESC}")
                quantity: int = Field(..., description=f"{GENERIC_QUANTITY_DESC}")
                unit_price: float = Field(..., description=f"{GENERIC_UNIT_PRICE_DESC}")
                deadline: str = Field(..., description=f"{GENERIC_DEADLINE_DESC}")

            class Order(BaseModel):
                number: str = Field(..., description=f"{GENERIC_NUMBER_DESC}")
                items: List[Item] = Field(..., description=f"{GENERIC_ITEMS_DESC}")

            return Order

    raise ValueError(f"Unknown client: {client.name}")
