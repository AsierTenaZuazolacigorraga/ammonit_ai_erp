import uuid
from datetime import datetime, timezone
from typing import Any

from app.api.deps import CurrentUserDep, OfferServiceDep
from app.models import Message, OfferCreate, OfferPublic, OffersPublic, OfferUpdate
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/", response_model=OffersPublic)
def read_offers(
    offer_service: OfferServiceDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
) -> OffersPublic:
    """
    Retrieve offers.
    """
    offers = offer_service.get_all(skip=skip, limit=limit, owner_id=current_user.id)
    count = offer_service.get_count(owner_id=current_user.id)

    offers_public = []
    for offer in offers:
        offers_public.append(OfferPublic.model_validate(offer))

    return OffersPublic(
        data=offers_public,
        count=count,
    )


@router.get("/{id}/", response_model=OfferPublic)
def read_offer(
    offer_service: OfferServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
) -> OfferPublic:
    """
    Get offer by id.
    """
    offer = offer_service.get_by_id(id)
    if not offer:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if not current_user.is_superuser and (offer.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    return OfferPublic.model_validate(offer)


@router.post("/", response_model=OfferPublic)
def create_offer(
    offer_service: OfferServiceDep,
    current_user: CurrentUserDep,
) -> OfferPublic:
    """
    Create an offer.
    """
    offer = offer_service.create(
        offer_create=OfferCreate(),
        owner_id=current_user.id,
    )
    return OfferPublic.model_validate(offer)


@router.delete("/{id}/")
def delete_offer(
    offer_service: OfferServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
) -> Message:
    """
    Delete an offer.
    """
    offer = offer_service.get_by_id(id)
    if not offer:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if not current_user.is_superuser and (offer.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    offer_service.delete(id)
    return Message(message="Documento eliminado correctamente")
