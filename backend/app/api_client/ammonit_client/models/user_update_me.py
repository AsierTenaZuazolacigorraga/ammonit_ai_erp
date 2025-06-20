from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserUpdateMe")


@_attrs_define
class UserUpdateMe:
    """
    Attributes:
        full_name (Union[None, Unset, str]):
        email (Union[None, Unset, str]):
        is_auto_approved (Union[Unset, bool]):  Default: False.
    """

    full_name: Union[None, Unset, str] = UNSET
    email: Union[None, Unset, str] = UNSET
    is_auto_approved: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        full_name: Union[None, Unset, str]
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        email: Union[None, Unset, str]
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email

        is_auto_approved = self.is_auto_approved

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if email is not UNSET:
            field_dict["email"] = email
        if is_auto_approved is not UNSET:
            field_dict["is_auto_approved"] = is_auto_approved

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_full_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

        def _parse_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email = _parse_email(d.pop("email", UNSET))

        is_auto_approved = d.pop("is_auto_approved", UNSET)

        user_update_me = cls(
            full_name=full_name,
            email=email,
            is_auto_approved=is_auto_approved,
        )

        user_update_me.additional_properties = d
        return user_update_me

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
