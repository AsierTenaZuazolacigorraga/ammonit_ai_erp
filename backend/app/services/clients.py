import uuid

from app.models import Client, ClientCreate, ClientUpdate
from app.repositories.clients import ClientRepository


class ClientService:
    def __init__(
        self,
        repository: ClientRepository,
    ) -> None:
        self.repository = repository

    def create(self, *, client_create: ClientCreate, owner_id: uuid.UUID) -> Client:
        db_obj = Client.model_validate(client_create, update={"owner_id": owner_id})
        return self.repository.create(db_obj)

    def get_all_by_owner_id(
        self, *, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Client]:
        return self.repository.get_all_by_owner_id(
            owner_id=owner_id, skip=skip, limit=limit
        )

    def count_by_owner_id(self, owner_id: uuid.UUID) -> int:
        return self.repository.count_by_owner_id(owner_id=owner_id)

    def update(self, *, db_client: Client, client_update: ClientUpdate) -> Client:
        db_obj = db_client.model_copy(update=client_update.model_dump())
        return self.repository.update(db_obj, update=client_update)
