import uuid

from app.core.config import settings
from app.models import Client, ClientCreate, ClientUpdate, OrderCreate
from app.repositories.base import CRUDRepository
from app.services.users import UserService
from openai import OpenAI
from pydantic import BaseModel
from sqlmodel import Session

ClientExample = Client(
    name="",
    clasifier="",
    base_document=b"",
    base_document_name="",
    base_document_markdown="",
    content_processed="",
    structure={
        "name": "order",
        "schema": {
            "type": "object",
            "properties": {
                "number": {"type": "string", "description": "The number of the order"},
                "items": {
                    "type": "array",
                    "description": "The items in the order",
                    "items": {"$ref": "#/$defs/item"},
                },
            },
            "required": ["number", "items"],
            "additionalProperties": False,
            "$defs": {
                "item": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code of the item",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the item",
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "The quantity of items to order",
                        },
                        "unit_price": {
                            "type": "number",
                            "description": "The unit price of the item",
                        },
                        "deadline": {
                            "type": "string",
                            "description": "The deadline or due date for the item",
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
    },
    additional_info="",
    owner_id=uuid.uuid4(),
)


class ClientService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Client](Client, session)
        self.user_service = UserService(session)

        # Initialize clients
        self.ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def create(self, client_create: ClientCreate, owner_id: uuid.UUID) -> Client:
        return self.repository.create(
            Client.model_validate(client_create, update={"owner_id": owner_id})
        )

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Client]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Client:
        client = self.repository.get_by_id(id)
        if not client:
            raise ValueError("Client not found")
        return client

    def get_count(self, owner_id: uuid.UUID) -> int:
        return self.repository.count_by_kwargs(**{"owner_id": owner_id})

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)

    def update(self, client_update: ClientUpdate, id: uuid.UUID) -> Client:
        client = self.get_by_id(id)
        if not client:
            raise ValueError("Client not found")
        return self.repository.update(
            client, update=client_update.model_dump(exclude_unset=True)
        )

    async def get_proposal(
        self, base_document: bytes, base_document_name: str, id: uuid.UUID
    ) -> Client:

        from app.services.orders import process

        client_proposal = ClientExample.model_copy(
            update={
                "owner_id": id,
                "base_document": base_document,
                "base_document_name": base_document_name,
            }
        )

        user, client, order = await process(
            order_create=OrderCreate(
                base_document=base_document,
                base_document_name=base_document_name,
            ),
            ai_client=self.ai_client,
            clients=[client_proposal],
            user=self.user_service.get_by_id(id),
        )
        return client

    def get_clasification_prompt(self, owner_id: uuid.UUID) -> str:

        from app.services._clients._clasifiers import _get_clasification_prompt

        user = self.user_service.get_by_id(owner_id)
        clients = self.get_all(skip=0, limit=100, owner_id=owner_id)
        return _get_clasification_prompt(user, clients)

    def get_structure(self, id: uuid.UUID) -> type[BaseModel]:

        from app.services._clients._structures import _get_client_structure

        client = self.get_by_id(id)
        user = self.user_service.get_by_id(client.owner_id)
        return _get_client_structure(user, client)
