import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserCreate")


@_attrs_define
class UserCreate:
    """
    Attributes:
        email (str):
        password (str):
        is_active (Union[Unset, bool]):  Default: True.
        is_superuser (Union[Unset, bool]):  Default: False.
        full_name (Union[None, Unset, str]):
        is_auto_approved (Union[Unset, bool]):  Default: False.
        created_at (Union[Unset, datetime.datetime]):
        orders_additional_rules (Union[None, Unset, str]):
        orders_particular_rules (Union[None, Unset, str]):
    """

    email: str
    password: str
    is_active: Union[Unset, bool] = True
    is_superuser: Union[Unset, bool] = False
    full_name: Union[None, Unset, str] = UNSET
    is_auto_approved: Union[Unset, bool] = False
    created_at: Union[Unset, datetime.datetime] = UNSET
    orders_additional_rules: Union[None, Unset, str] = UNSET
    orders_particular_rules: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        password = self.password

        is_active = self.is_active

        is_superuser = self.is_superuser

        full_name: Union[None, Unset, str]
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        is_auto_approved = self.is_auto_approved

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        orders_additional_rules: Union[None, Unset, str]
        if isinstance(self.orders_additional_rules, Unset):
            orders_additional_rules = UNSET
        else:
            orders_additional_rules = self.orders_additional_rules

        orders_particular_rules: Union[None, Unset, str]
        if isinstance(self.orders_particular_rules, Unset):
            orders_particular_rules = UNSET
        else:
            orders_particular_rules = self.orders_particular_rules

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "password": password,
            }
        )
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if is_superuser is not UNSET:
            field_dict["is_superuser"] = is_superuser
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if is_auto_approved is not UNSET:
            field_dict["is_auto_approved"] = is_auto_approved
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if orders_additional_rules is not UNSET:
            field_dict["orders_additional_rules"] = orders_additional_rules
        if orders_particular_rules is not UNSET:
            field_dict["orders_particular_rules"] = orders_particular_rules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        password = d.pop("password")

        is_active = d.pop("is_active", UNSET)

        is_superuser = d.pop("is_superuser", UNSET)

        def _parse_full_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

        is_auto_approved = d.pop("is_auto_approved", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_orders_additional_rules(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        orders_additional_rules = _parse_orders_additional_rules(d.pop("orders_additional_rules", UNSET))

        def _parse_orders_particular_rules(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        orders_particular_rules = _parse_orders_particular_rules(d.pop("orders_particular_rules", UNSET))

        user_create = cls(
            email=email,
            password=password,
            is_active=is_active,
            is_superuser=is_superuser,
            full_name=full_name,
            is_auto_approved=is_auto_approved,
            created_at=created_at,
            orders_additional_rules=orders_additional_rules,
            orders_particular_rules=orders_particular_rules,
        )

        user_create.additional_properties = d
        return user_create

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
