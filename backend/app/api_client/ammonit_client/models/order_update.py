import datetime
from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.order_state import OrderState
from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="OrderUpdate")


@_attrs_define
class OrderUpdate:
    """
    Attributes:
        base_document (Union[File, None, Unset]):
        base_document_name (Union[None, Unset, str]):
        content_processed (Union[None, Unset, str]):
        state (Union[Unset, OrderState]):
        approved_at (Union[None, Unset, datetime.datetime]):
        created_in_erp_at (Union[None, Unset, datetime.datetime]):
        created_at (Union[Unset, datetime.datetime]):
    """

    base_document: Union[File, None, Unset] = UNSET
    base_document_name: Union[None, Unset, str] = UNSET
    content_processed: Union[None, Unset, str] = UNSET
    state: Union[Unset, OrderState] = UNSET
    approved_at: Union[None, Unset, datetime.datetime] = UNSET
    created_in_erp_at: Union[None, Unset, datetime.datetime] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_document: Union[FileJsonType, None, Unset]
        if isinstance(self.base_document, Unset):
            base_document = UNSET
        elif isinstance(self.base_document, File):
            base_document = self.base_document.to_tuple()

        else:
            base_document = self.base_document

        base_document_name: Union[None, Unset, str]
        if isinstance(self.base_document_name, Unset):
            base_document_name = UNSET
        else:
            base_document_name = self.base_document_name

        content_processed: Union[None, Unset, str]
        if isinstance(self.content_processed, Unset):
            content_processed = UNSET
        else:
            content_processed = self.content_processed

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        approved_at: Union[None, Unset, str]
        if isinstance(self.approved_at, Unset):
            approved_at = UNSET
        elif isinstance(self.approved_at, datetime.datetime):
            approved_at = self.approved_at.isoformat()
        else:
            approved_at = self.approved_at

        created_in_erp_at: Union[None, Unset, str]
        if isinstance(self.created_in_erp_at, Unset):
            created_in_erp_at = UNSET
        elif isinstance(self.created_in_erp_at, datetime.datetime):
            created_in_erp_at = self.created_in_erp_at.isoformat()
        else:
            created_in_erp_at = self.created_in_erp_at

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if base_document is not UNSET:
            field_dict["base_document"] = base_document
        if base_document_name is not UNSET:
            field_dict["base_document_name"] = base_document_name
        if content_processed is not UNSET:
            field_dict["content_processed"] = content_processed
        if state is not UNSET:
            field_dict["state"] = state
        if approved_at is not UNSET:
            field_dict["approved_at"] = approved_at
        if created_in_erp_at is not UNSET:
            field_dict["created_in_erp_at"] = created_in_erp_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_base_document(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                base_document_type_0 = File(payload=BytesIO(data))

                return base_document_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

        base_document = _parse_base_document(d.pop("base_document", UNSET))

        def _parse_base_document_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_document_name = _parse_base_document_name(d.pop("base_document_name", UNSET))

        def _parse_content_processed(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        content_processed = _parse_content_processed(d.pop("content_processed", UNSET))

        _state = d.pop("state", UNSET)
        state: Union[Unset, OrderState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = OrderState(_state)

        def _parse_approved_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                approved_at_type_0 = isoparse(data)

                return approved_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        approved_at = _parse_approved_at(d.pop("approved_at", UNSET))

        def _parse_created_in_erp_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_in_erp_at_type_0 = isoparse(data)

                return created_in_erp_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        created_in_erp_at = _parse_created_in_erp_at(d.pop("created_in_erp_at", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        order_update = cls(
            base_document=base_document,
            base_document_name=base_document_name,
            content_processed=content_processed,
            state=state,
            approved_at=approved_at,
            created_in_erp_at=created_in_erp_at,
            created_at=created_at,
        )

        order_update.additional_properties = d
        return order_update

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
