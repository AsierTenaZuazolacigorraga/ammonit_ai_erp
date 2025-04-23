import uuid
from datetime import datetime, timezone
from typing import Any

from app.api.deps import CurrentUser, OrderServiceDep
from app.models import (
    Message,
    Order,
    OrderCreate,
    OrderPublic,
    OrdersPublic,
    OrderUpdate,
)
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=OrdersPublic)
def read_orders(
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> OrdersPublic:
    """
    Retrieve orders.
    """
    count = order_service.repository.count_by_owner_id(owner_id=current_user.id)
    orders = order_service.repository.get_all_by_owner_id(
        owner_id=current_user.id, skip=skip, limit=limit
    )
    # Convert Order objects to OrderPublic objects
    order_publics = [OrderPublic.model_validate(order) for order in orders]
    return OrdersPublic(data=order_publics, count=count)


@router.get("/{id}/", response_model=OrderPublic)
def read_order(
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> OrderPublic:
    """
    Get order by id.
    """
    order = order_service.repository.get_by_id(id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    # Convert Order object to OrderPublic object
    return OrderPublic.model_validate(order)


@router.post("/", response_model=OrderPublic)
async def create_order(
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    base_document: UploadFile = File(...),
) -> OrderPublic:
    """
    Create an order.
    """
    file_bytes: bytes = await base_document.read()

    order_data = OrderCreate(
        base_document=file_bytes,
        base_document_name=base_document.filename,
    )

    order = await order_service.create(
        order_create=order_data, owner_id=current_user.id
    )
    return OrderPublic.model_validate(order)


@router.delete("/{id}/")
def delete_order(
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Message:
    """
    Delete an order.
    """
    order = order_service.repository.get_by_id(id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    order_service.repository.delete(id)
    return Message(message="Pedido eliminado correctamente")


@router.patch(
    "/{id}/",
    response_model=OrderPublic,
)
def update_order(
    *,
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    order_in: OrderUpdate,
) -> OrderPublic:
    """
    Update an order.
    """

    order = order_service.repository.get_by_id(id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")

    order = order_service.update(db_order=order, order_update=order_in)
    return OrderPublic.model_validate(order)
