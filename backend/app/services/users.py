import uuid

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate, UserUpdateMe
from app.repositories.base import CRUDRepository
from sqlmodel import Session, select


class UserService:
    def __init__(self, session: Session) -> None:
        self.repository = CRUDRepository[User](User, session)

    def create(self, *, user_create: UserCreate) -> User:
        return self.repository.create(
            User.model_validate(
                user_create,
                update={"hashed_password": get_password_hash(user_create.password)},
            )
        )

    def get_all(self, skip: int, limit: int) -> list[User]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
        )

    def get_count(self) -> int:
        return self.repository.count()

    def get_by_id(self, id: uuid.UUID) -> User:
        user = self.repository.get_by_id(id)
        if not user:
            raise ValueError("User not found")
        return user

    def get_by_email(self, email: str) -> User | None:
        users = self.repository.get_all_by_kwargs(email=email)
        if len(users) > 1:
            raise ValueError(f"Multiple users found with email {email}")
        return users[0] if users else None

    def update(self, user_update: UserUpdate | UserUpdateMe, id: uuid.UUID) -> User:
        user = self.get_by_id(id)
        if not user:
            raise ValueError("User not found")
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            password = update_data["password"]
            hashed_password = get_password_hash(password)
            update_data["hashed_password"] = hashed_password
        return self.repository.update(user, update=update_data)

    def authenticate(self, *, email: str, password: str) -> User:
        statement = select(User).where(User.email == email)
        user = self.repository.session.exec(statement).first()
        if not user:
            raise ValueError(f"User with email {email} not found")
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid password")
        return user

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)
