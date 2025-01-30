import base64
import uuid
from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Order,
    OrderCreate,
    OrderPublic,
    OrdersPublic,
    OrderUpdate,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=OrdersPublic)
def read_orders(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve orders.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Order)
        count = session.exec(count_statement).one()
        statement = select(Order).offset(skip).limit(limit)
        orders = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Order)
            .where(Order.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Order)
            .where(Order.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        orders = session.exec(statement).all()

    return OrdersPublic(data=orders, count=count)


@router.get("/{id}", response_model=OrderPublic)
def read_order(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get order by ID.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    return order


@router.post("/", response_model=OrderPublic)
def create_and_process_order(
    *, session: SessionDep, current_user: CurrentUser, order_in: OrderCreate
) -> Any:
    """
    Create and Process new order.
    """
    order = Order.model_validate(order_in, update={"owner_id": current_user.id})

    # Process order name
    def in_name_2_out_name(name: str) -> str:
        name, extension = name.rsplit(".", 1)
        return f"{name}_ammonit_processed.{extension}"

    order.out_document_name = in_name_2_out_name(order.in_document_name)

    # Process order content
    order.out_document = order.in_document

    # Save order in db
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.delete("/{id}")
def delete_order(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an order.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    session.delete(order)
    session.commit()
    return Message(message="Pedido eliminado correctamente")
