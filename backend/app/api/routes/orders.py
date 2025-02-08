import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, OrderServiceDep
from app.models import (
    Order,
    OrderCreate,
    OrderPublic,
    OrdersPublic,
    OrderUpdate,
    Message,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=OrdersPublic)
def read_orders(
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve orders.
    """
    count: int
    orders: list[Order]
    if current_user.is_superuser:
        count = order_service.repository.count()
        orders = order_service.repository.get_all(skip=skip, limit=limit)
    else:
        count = order_service.repository.count_by_owner_id(owner_id=current_user.id)
        orders = order_service.repository.get_all_by_owner_id(
            owner_id=current_user.id, skip=skip, limit=limit
        )

    return OrdersPublic(data=orders, count=count)


@router.get("/{id}", response_model=OrderPublic)
def read_order(
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """
    Get order by id.
    """
    order = order_service.repository.get_by_id(id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    return order


@router.post("/", response_model=OrderPublic)
def create_order(
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    order_in: OrderCreate,
) -> Any:
    """
    Create new order.
    """
    order = order_service.create(order_create=order_in, owner_id=current_user.id)
    return order


@router.put("/{id}", response_model=OrderPublic)
def update_order(
    *,
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    order_in: OrderUpdate,
) -> Any:
    """
    Update an order.
    """
    order = order_service.repository.get_by_id(id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    update_dict = order_in.model_dump(exclude_unset=True)
    order = order_service.repository.update(order, update=update_dict)
    return order


@router.delete("/{id}")
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
