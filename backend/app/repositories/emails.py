from app.models import Email
from app.repositories.base import CRUDRepository
from sqlmodel import Session


class EmailRepository(CRUDRepository[Email]):
    def __init__(self, session: Session) -> None:
        super().__init__(Email, session)
