import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailCreate")


@_attrs_define
class EmailCreate:
    """
    Attributes:
        email (str):
        is_orders (Union[Unset, bool]):  Default: False.
        orders_filter (Union[None, Unset, str]):
        is_offers (Union[Unset, bool]):  Default: False.
        offers_filter (Union[None, Unset, str]):
        created_at (Union[Unset, datetime.datetime]):
    """

    email: str
    is_orders: Union[Unset, bool] = False
    orders_filter: Union[None, Unset, str] = UNSET
    is_offers: Union[Unset, bool] = False
    offers_filter: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        is_orders = self.is_orders

        orders_filter: Union[None, Unset, str]
        if isinstance(self.orders_filter, Unset):
            orders_filter = UNSET
        else:
            orders_filter = self.orders_filter

        is_offers = self.is_offers

        offers_filter: Union[None, Unset, str]
        if isinstance(self.offers_filter, Unset):
            offers_filter = UNSET
        else:
            offers_filter = self.offers_filter

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
            }
        )
        if is_orders is not UNSET:
            field_dict["is_orders"] = is_orders
        if orders_filter is not UNSET:
            field_dict["orders_filter"] = orders_filter
        if is_offers is not UNSET:
            field_dict["is_offers"] = is_offers
        if offers_filter is not UNSET:
            field_dict["offers_filter"] = offers_filter
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        is_orders = d.pop("is_orders", UNSET)

        def _parse_orders_filter(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        orders_filter = _parse_orders_filter(d.pop("orders_filter", UNSET))

        is_offers = d.pop("is_offers", UNSET)

        def _parse_offers_filter(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        offers_filter = _parse_offers_filter(d.pop("offers_filter", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        email_create = cls(
            email=email,
            is_orders=is_orders,
            orders_filter=orders_filter,
            is_offers=is_offers,
            offers_filter=offers_filter,
            created_at=created_at,
        )

        email_create.additional_properties = d
        return email_create

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
