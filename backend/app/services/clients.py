import uuid

from app.models import Client, ClientCreate, ClientUpdate, OrderCreate
from app.repositories.base import CRUDRepository
from app.services.orders import OrderService
from app.services.users import UserService
from pydantic import BaseModel
from sqlmodel import Session


class ClientService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Client](Client, session)
        self.user_service = UserService(session)
        self.order_service = OrderService(session)

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
        self, base_document: bytes, base_document_name: str, owner_id: uuid.UUID
    ) -> Client:
        user = self.user_service.get_by_id(owner_id)
        clients = self.get_all(skip=0, limit=100, owner_id=owner_id)
        email_id = None
        order, client = await self.order_service.process(
            order_create=OrderCreate(
                base_document=base_document,
                base_document_name=base_document_name,
            ),
            user=user,
            clients=clients,
            email_id=email_id,
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
