import uuid

from app.models import Client, ClientCreate, ClientUpdate
from app.repositories.base import CRUDRepository
from sqlmodel import Session


class ClientService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository(Client, session)
        self.session = session
