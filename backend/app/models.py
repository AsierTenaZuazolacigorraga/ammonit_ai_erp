import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

##########################################################################################
# User
##########################################################################################


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


class User(UserBase, table=True):
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
    date: datetime = Field(nullable=False)  # For storing dates/times
    in_document: bytes | None = Field(
        default=None, nullable=False
    )  # For storing binary data (documents)
    out_document: bytes | None = Field(default=None, nullable=False)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    pass


class Order(OrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="orders")


class OrderPublic(OrderBase):
    id: uuid.UUID
    owner_id: uuid.UUID


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
