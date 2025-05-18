import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClientCreate")


@_attrs_define
class ClientCreate:
    """
    Attributes:
        name (str):
        clasifier (str):
        base_markdown (str):
        content_processed (str):
        created_at (Union[Unset, datetime.datetime]):
    """

    name: str
    clasifier: str
    base_markdown: str
    content_processed: str
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        clasifier = self.clasifier

        base_markdown = self.base_markdown

        content_processed = self.content_processed

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "clasifier": clasifier,
                "base_markdown": base_markdown,
                "content_processed": content_processed,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        clasifier = d.pop("clasifier")

        base_markdown = d.pop("base_markdown")

        content_processed = d.pop("content_processed")

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        client_create = cls(
            name=name,
            clasifier=clasifier,
            base_markdown=base_markdown,
            content_processed=content_processed,
            created_at=created_at,
        )

        client_create.additional_properties = d
        return client_create

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
