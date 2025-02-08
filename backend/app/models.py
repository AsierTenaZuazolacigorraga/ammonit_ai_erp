import base64
import uuid
from datetime import datetime, timezone

from pydantic import EmailStr, model_validator
from sqlmodel import Field, Relationship, SQLModel

##########################################################################################
# User
##########################################################################################


class Entity(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(Entity, UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    orders: list["Order"] = Relationship(back_populates="owner", cascade_delete=True)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


##########################################################################################
# Order
##########################################################################################


class OrderBase(SQLModel):
    date_local: datetime = Field(nullable=False)
    date_utc: datetime = Field(nullable=False)
    in_document: bytes | None = Field(
        default=None, nullable=False
    )  # For storing binary data (documents)
    in_document_name: str | None = Field(default=None, max_length=255)
    out_document: bytes | None = Field(default=None, nullable=False)
    out_document_name: str | None = Field(default=None, max_length=255)


class OrderCreate(OrderBase):
    in_document_base64: str | None = Field(default=None)

    @model_validator(mode="before")
    def decode_documents(cls, values):
        if "in_document_base64" in values:
            values["in_document"] = base64.b64decode(
                values["in_document_base64"]
            )  # Convert Base64 to binary
        return values


class OrderUpdate(OrderBase):
    pass


class Order(Entity, OrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="orders")


class OrderPublic(OrderBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    in_document: str | None = Field(default=None)
    out_document: str | None = Field(default=None)
    # Expect Base64-encoded string from client
    # For example, this string "U29tZSBkYXRhIHN0cmluZw==" is a representatio fo this data b'Some data string'
    # This class should return the "" and not the b''

    @model_validator(mode="before")
    def encode_documents(cls, values):
        if values.in_document:
            values.in_document = base64.b64encode(values.in_document).decode("utf-8")
        if values.out_document:
            values.out_document = base64.b64encode(values.out_document).decode("utf-8")
        return values


class OrdersPublic(SQLModel):
    data: list[OrderPublic]
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
