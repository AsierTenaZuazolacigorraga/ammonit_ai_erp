import uuid

from app.models import Order, OrderCreate
from app.repositories.orders import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def create(self, *, order_create: OrderCreate, owner_id: uuid.UUID) -> Order:
        db_obj = Order.model_validate(order_create, update={"owner_id": owner_id})
        return self.repository.create(db_obj)
