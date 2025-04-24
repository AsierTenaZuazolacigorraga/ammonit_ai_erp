import base64
import uuid
from datetime import datetime, timezone

from pydantic import EmailStr, model_validator
from sqlmodel import Field, Relationship, SQLModel


class Entity(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


##########################################################################################
# User
##########################################################################################


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    is_auto_approved: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    is_auto_approved: bool = False


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(Entity, UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    clients: list["Client"] = Relationship(back_populates="owner", cascade_delete=True)
    emails: list["Email"] = Relationship(back_populates="owner", cascade_delete=True)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


##########################################################################################
# Clients
##########################################################################################


class ClientBase(SQLModel):
    name: str = Field(nullable=False)
    clasifier: str = Field(nullable=False)
    structure: str = Field(nullable=False)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class Client(Entity, ClientBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="clients")
    orders: list["Order"] = Relationship(back_populates="owner", cascade_delete=True)


class ClientPublic(ClientBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ClientsPublic(SQLModel):
    data: list[ClientPublic]
    count: int


##########################################################################################
# Order
##########################################################################################


class OrderBase(SQLModel):
    base_document: bytes | None = Field(default=None, nullable=False)
    base_document_name: str | None = Field(default=None, max_length=255)
    date_processed: datetime | None = Field(default=None)  # In utc
    date_approved: datetime | None = Field(default=None)  # In utc
    is_approved: bool | None = Field(default=None)
    content_processed: str | None = Field(default=None)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    pass


class Order(Entity, OrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="client.id", nullable=False, ondelete="CASCADE"
    )
    owner: Client | None = Relationship(back_populates="orders")


class OrderPublic(OrderBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    base_document: str | None = Field(
        default=None, nullable=False
    )  # Override base_document to be a string (base64 encoded) for JSON serialization
    client_name: str | None = Field(default=None)

    @classmethod
    def model_validate(cls, obj):
        obj_dict = obj.model_dump()
        if obj_dict.get("base_document") is not None:
            obj_dict["base_document"] = base64.b64encode(
                obj_dict["base_document"]
            ).decode("utf-8")
        return cls(**obj_dict)


class OrdersPublic(SQLModel):
    data: list[OrderPublic]
    count: int


##########################################################################################
# Emails
##########################################################################################


class EmailBase(SQLModel):
    email_id: str = Field(nullable=False)
    is_processed: bool = Field(default=False)


class EmailCreate(EmailBase):
    pass


class Email(Entity, EmailBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="emails")


class EmailPublic(OrderBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class EmailsPublic(SQLModel):
    data: list[EmailPublic]
    count: int


##########################################################################################
# Others
##########################################################################################


class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
