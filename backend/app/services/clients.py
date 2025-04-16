import uuid

from app.models import Client, ClientCreate
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
