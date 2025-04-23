import uuid

from app.models import Client, ClientCreate, ClientUpdate
from app.repositories.clients import ClientRepository


class ClientService:
    def __init__(
        self,
        repository: ClientRepository,
    ) -> None:
        self.repository = repository
