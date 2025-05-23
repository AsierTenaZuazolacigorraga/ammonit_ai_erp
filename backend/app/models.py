import base64
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Type, TypeVar, Union

from pydantic import EmailStr, model_validator
from sqlalchemy import JSON, Column
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel._compat import sqlmodel_validate


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
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )


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
    base_document: bytes | None = Field(default=None, nullable=False)
    base_document_name: str | None = Field(default=None, max_length=255)
    base_document_markdown: str | None = Field(default=None)
    content_processed: str | None = Field(default=None)
    clasifier: str = Field(nullable=False)
    structure: dict = Field(sa_column=Column(JSON, nullable=False))
    additional_info: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )


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

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: Union[bool, None] = None,
        from_attributes: Union[bool, None] = None,
        context: Union[Dict[str, Any], None] = None,
        update: Union[Dict[str, Any], None] = None,
    ):
        obj_dict = obj.model_dump()
        if obj_dict.get("base_document") is not None:
            obj_dict["base_document"] = base64.b64encode(
                obj_dict["base_document"]
            ).decode("utf-8")
        return sqlmodel_validate(
            cls=cls,
            obj=cls(**obj_dict),
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            update=update,
        )


class ClientsPublic(SQLModel):
    data: list[ClientPublic]
    count: int


##########################################################################################
# Order
##########################################################################################


class OrderState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    INTEGRATED_OK = "INTEGRATED_OK"
    INTEGRATED_ERROR = "INTEGRATED_ERROR"


class OrderBase(SQLModel):
    base_document: bytes | None = Field(default=None, nullable=False)
    base_document_name: str | None = Field(default=None, max_length=255)
    base_document_markdown: str | None = Field(default=None)
    content_processed: str | None = Field(default=None)
    state: OrderState = Field(
        sa_column=Column(
            PGEnum(OrderState, name="order_state_enum", create_type=True),
            nullable=False,
        ),
        default=OrderState.PENDING,
    )
    approved_at: datetime | None = Field(default=None, nullable=True)  # In UTC
    created_in_erp_at: datetime | None = Field(default=None, nullable=True)  # In UTC
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )  # In UTC


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    pass


class Order(Entity, OrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="client.id", nullable=False, ondelete="CASCADE"
    )
    email_id: uuid.UUID | None = Field(
        foreign_key="email.id", nullable=True, ondelete="SET NULL"
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
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: Union[bool, None] = None,
        from_attributes: Union[bool, None] = None,
        context: Union[Dict[str, Any], None] = None,
        update: Union[Dict[str, Any], None] = None,
    ):
        obj_dict = obj.model_dump()
        if obj_dict.get("base_document") is not None:
            obj_dict["base_document"] = base64.b64encode(
                obj_dict["base_document"]
            ).decode("utf-8")
        return sqlmodel_validate(
            cls=cls,
            obj=cls(**obj_dict),
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            update=update,
        )


class OrdersPublic(SQLModel):
    data: list[OrderPublic]
    count: int


##########################################################################################
# Emails
##########################################################################################


class EmailBase(SQLModel):
    email: str = Field(nullable=False)
    filter: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )


class EmailCreate(EmailBase):
    pass


class EmailUpdate(EmailBase):
    pass


class Email(Entity, EmailBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="emails")
    emails_data: list["EmailData"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


class EmailPublic(EmailBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    is_connected: bool = Field(default=False)


class EmailsPublic(SQLModel):
    data: list[EmailPublic]
    count: int


class EmailDataState(str, Enum):
    PROCESSED_OK = "PROCESSED_OK"
    PROCESSED_ERROR = "PROCESSED_ERROR"


class EmailDataBase(SQLModel):
    email_id: str = Field(nullable=False)
    email_body: str | None = Field(default=None)
    state: EmailDataState = Field(
        sa_column=Column(
            PGEnum(EmailDataState, name="email_state_enum", create_type=True),
            nullable=False,
        ),
        default=EmailDataState.PROCESSED_OK,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )


class EmailDataCreate(EmailDataBase):
    pass


class EmailData(Entity, EmailDataBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="email.id", nullable=False, ondelete="CASCADE"
    )
    owner: Email | None = Relationship(back_populates="emails_data")


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
