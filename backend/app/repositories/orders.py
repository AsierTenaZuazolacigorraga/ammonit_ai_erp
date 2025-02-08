from uuid import UUID

from sqlmodel import Session

from app.models import Order
from app.repositories.base import CRUDRepository


class OrderRepository(CRUDRepository[Order]):
    def __init__(self, session: Session) -> None:
        super().__init__(Order, session)

    def count_by_owner_id(self, owner_id: UUID) -> int:
        return self.count_by_kwargs(**{"owner_id": owner_id})

    def get_all_by_owner_id(
        self, *, owner_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Order]:
        return self.get_all_by_kwargs(skip=skip, limit=limit, **{"owner_id": owner_id})
