import uuid
from datetime import datetime, timezone

from app.logger import get_logger
from app.models import Offer, OfferCreate, OfferState, OfferUpdate, User
from app.repositories.base import CRUDRepository
from app.services.ai import AiService
from app.services.users import UserService
from sqlmodel import Session

logger = get_logger(__name__)


class OfferService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Offer](Offer, session)
        self.user_service = UserService(session)
        self.ai_service = AiService(session)

    def create(
        self,
        offer_create: OfferCreate,
        owner_id: uuid.UUID,
        email_id: uuid.UUID | None = None,
    ) -> Offer:

        # Get from external service
        user = self.user_service.get_by_id(owner_id)

        # Adapt the ids
        update = {"owner_id": user.id, "email_id": email_id}
        offer = Offer.model_validate(offer_create, update=update)

        # Timestamp
        offer.state_set_at = {
            OfferState.PENDING.value: datetime.now(timezone.utc).isoformat()
        }

        # Create the offer
        self.repository.create(offer)

        # Approve the offer (if needed)
        if user and user.is_auto_approved:
            offer = self.approve(offer_update=OfferUpdate(), id=offer.id, user=user)

        return offer

    def update(self, offer_update: OfferUpdate, id: uuid.UUID) -> Offer:
        offer = self.get_by_id(id)
        return self.repository.update(
            offer, update=offer_update.model_dump(exclude_unset=True)
        )

    def adapt_state(
        self,
        offer_update: OfferUpdate,
        new_state: OfferState,
    ) -> OfferUpdate:

        current_time = datetime.now(timezone.utc).isoformat()

        # Initialize state_set_at if it doesn't exist
        if offer_update.state_set_at is None:
            offer_update.state_set_at = {}

        # Update the state timestamps using enum value
        offer_update.state_set_at[new_state.value] = current_time

        # Update the order state
        offer_update.state = new_state

        return offer_update

    def approve(self, offer_update: OfferUpdate, id: uuid.UUID, user: User) -> Offer:

        from app.services._offers._postprocessors_offers import _postprocess_offer

        state = _postprocess_offer(user)

        # Adaptations
        offer_update = self.adapt_state(offer_update, state)

        return self.update(offer_update, id)

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Offer]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Offer:
        offer = self.repository.get_by_id(id)
        if offer is None:
            raise ValueError("Offer not found")
        return offer

    def get_count(self, owner_id: uuid.UUID) -> int:
        return self.repository.count_by_kwargs(**{"owner_id": owner_id})

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)
