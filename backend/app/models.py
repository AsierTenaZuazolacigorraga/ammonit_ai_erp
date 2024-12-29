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
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    machines: list["Machine"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


##########################################################################################
# Machine
##########################################################################################


class MachineBase(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    provider: str | None = Field(default=None, max_length=255)
    plc: str | None = Field(default=None, max_length=255)
    oee: float
    oee_availability: float
    oee_performance: float
    oee_quality: float


class MachineCreate(MachineBase):
    pass


class MachineUpdate(MachineBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class Machine(MachineBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="machines")
    measurements: list["Measurement"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


class MachinePublic(MachineBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class MachinesPublic(SQLModel):
    data: list[MachinePublic]
    count: int


##########################################################################################
# Measurement
##########################################################################################


class MeasurementBase(SQLModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    temperature: float
    power_usage: float


class MeasurementCreate(MeasurementBase):
    owner_id: uuid.UUID  # Id of the machine


class MeasurementUpdate(MeasurementBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class Measurement(MeasurementBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="machine.id", nullable=False, ondelete="CASCADE"
    )
    owner: Machine | None = Relationship(back_populates="measurements")


class MeasurementPublic(MeasurementBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class MeasurementsPublic(SQLModel):
    data: list[MeasurementPublic]
    count: int


##########################################################################################
# Item
##########################################################################################


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
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
