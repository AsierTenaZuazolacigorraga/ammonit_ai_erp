from app.api.routes import emails, login, offers, orders, users, utils  # private
from app.core.config import settings
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(orders.router)
api_router.include_router(emails.router)
api_router.include_router(offers.router)
