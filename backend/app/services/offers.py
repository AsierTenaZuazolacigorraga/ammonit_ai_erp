import uuid

from app.logger import get_logger
from app.models import Offer, OfferCreate, OfferUpdate
from app.repositories.base import CRUDRepository
from app.services.ai import AiService
from sqlmodel import Session

logger = get_logger(__name__)


class OfferService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Offer](Offer, session)
        self.ai_service = AiService(session)

    def create(
        self,
        offer_create: OfferCreate,
        owner_id: uuid.UUID,
        email_id: uuid.UUID | None = None,
    ) -> Offer:
        return self.repository.create(
            Offer.model_validate(
                offer_create,
                update={
                    "owner_id": owner_id,
                    "is_connected": False,
                    "email_id": email_id,
                },
            )
        )

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Offer]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Offer | None:
        return self.repository.get_by_id(id)

    def get_count(self, owner_id: uuid.UUID) -> int:
        return self.repository.count_by_kwargs(**{"owner_id": owner_id})

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)
