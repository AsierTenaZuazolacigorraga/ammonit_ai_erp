import uuid
from typing import Any

from app.api.deps import ClientServiceDep, CurrentUser
from app.models import Client, ClientCreate, ClientPublic, ClientsPublic
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=ClientsPublic)
def read_clients(
    client_service: ClientServiceDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve clients.
    """
    count = client_service.repository.count_by_owner_id(owner_id=current_user.id)
    clients = client_service.repository.get_all_by_owner_id(
        owner_id=current_user.id, skip=skip, limit=limit
    )
    return ClientsPublic(data=clients, count=count)


@router.post("/", response_model=ClientPublic)
def create_client(
    client_service: ClientServiceDep,
    current_user: CurrentUser,
    client_in: ClientCreate,
) -> Any:
    """
    Create new client.
    """
    client = client_service.create(client_create=client_in, owner_id=current_user.id)
    return client
