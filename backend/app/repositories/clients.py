from uuid import UUID

from app.models import Client
from app.repositories.base import CRUDRepository
from sqlmodel import Session


class ClientRepository(CRUDRepository[Client]):
    def __init__(self, session: Session) -> None:
        super().__init__(Client, session)

    def count_by_owner_id(self, owner_id: UUID) -> int:
        return self.count_by_kwargs(**{"owner_id": owner_id})

    def get_all_by_owner_id(
        self, *, owner_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Client]:
        return self.get_all_by_kwargs(skip=skip, limit=limit, **{"owner_id": owner_id})
