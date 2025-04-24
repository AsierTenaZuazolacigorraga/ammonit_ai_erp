import uuid

from app.models import Client, ClientCreate, ClientUpdate
from app.repositories.base import CRUDRepository
from sqlmodel import Session


class ClientService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Client](Client, session)

    def create(self, client_create: ClientCreate, owner_id: uuid.UUID) -> Client:
        return self.repository.create(
            Client.model_validate(client_create, update={"owner_id": owner_id})
        )

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Client]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            order_by=self.repository.table.id,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Client | None:
        return self.repository.get_by_id(id)

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
