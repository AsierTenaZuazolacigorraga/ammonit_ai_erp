import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailPublic")


@_attrs_define
class EmailPublic:
    """
    Attributes:
        email (str):
        id (UUID):
        owner_id (UUID):
        created_at (Union[Unset, datetime.datetime]):
        is_connected (Union[Unset, bool]):  Default: False.
    """

    email: str
    id: UUID
    owner_id: UUID
    created_at: Union[Unset, datetime.datetime] = UNSET
    is_connected: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        id = str(self.id)

        owner_id = str(self.owner_id)

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        is_connected = self.is_connected

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "id": id,
                "owner_id": owner_id,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if is_connected is not UNSET:
            field_dict["is_connected"] = is_connected

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        id = UUID(d.pop("id"))

        owner_id = UUID(d.pop("owner_id"))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        is_connected = d.pop("is_connected", UNSET)

        email_public = cls(
            email=email,
            id=id,
            owner_id=owner_id,
            created_at=created_at,
            is_connected=is_connected,
        )

        email_public.additional_properties = d
        return email_public

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
