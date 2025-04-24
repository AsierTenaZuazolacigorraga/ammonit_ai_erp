import uuid
from typing import Any

from app.api.deps import ClientServiceDep, CurrentUserDep
from app.models import (
    Client,
    ClientCreate,
    ClientPublic,
    ClientsPublic,
    ClientUpdate,
    Message,
)
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=ClientsPublic)
def read_clients(
    client_service: ClientServiceDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
) -> ClientsPublic:
    """
    Retrieve clients.
    """
    clients = client_service.repository.get_all_by_kwargs(
        skip=skip, limit=limit, **{"owner_id": current_user.id}
    )
    count = client_service.repository.count_by_kwargs(**{"owner_id": current_user.id})
    # Convert Client objects to ClientPublic objects
    client_publics = [ClientPublic.model_validate(client) for client in clients]
    return ClientsPublic(data=client_publics, count=count)


@router.post("/", response_model=ClientPublic)
def create_client(
    client_service: ClientServiceDep,
    current_user: CurrentUserDep,
    client_in: ClientCreate,
) -> ClientPublic:
    """
    Create new client.
    """
    client = client_service.create(client_create=client_in, owner_id=current_user.id)
    return ClientPublic.model_validate(client)


@router.delete("/{id}/")
def delete_client(
    client_service: ClientServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
) -> Message:
    """
    Delete an client.
    """
    client = client_service.repository.get_by_id(id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if not current_user.is_superuser and (client.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    client_service.repository.delete(id)
    return Message(message="Cliente eliminado correctamente")


@router.patch(
    "/{id}/",
    response_model=ClientPublic,
)
def update_client(
    *,
    client_service: ClientServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
    client_in: ClientUpdate,
) -> ClientPublic:
    """
    Update a client.
    """

    client = client_service.repository.get_by_id(id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if not current_user.is_superuser and (client.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")

    client = client_service.update(db_client=client, client_update=client_in)
    return ClientPublic.model_validate(client)
