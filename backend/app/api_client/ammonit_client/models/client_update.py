import datetime
from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, File, FileJsonType, Unset

if TYPE_CHECKING:
    from ..models.client_update_structure import ClientUpdateStructure
    from ..models.client_update_structure_descriptions import ClientUpdateStructureDescriptions


T = TypeVar("T", bound="ClientUpdate")


@_attrs_define
class ClientUpdate:
    """
    Attributes:
        name (str):
        clasifier (str):
        structure (ClientUpdateStructure):
        structure_descriptions (ClientUpdateStructureDescriptions):
        base_document (Union[File, None, Unset]):
        base_document_name (Union[None, Unset, str]):
        base_document_markdown (Union[None, Unset, str]):
        content_processed (Union[None, Unset, str]):
        additional_info (Union[None, Unset, str]):
        created_at (Union[Unset, datetime.datetime]):
    """

    name: str
    clasifier: str
    structure: "ClientUpdateStructure"
    structure_descriptions: "ClientUpdateStructureDescriptions"
    base_document: Union[File, None, Unset] = UNSET
    base_document_name: Union[None, Unset, str] = UNSET
    base_document_markdown: Union[None, Unset, str] = UNSET
    content_processed: Union[None, Unset, str] = UNSET
    additional_info: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        clasifier = self.clasifier

        structure = self.structure.to_dict()

        structure_descriptions = self.structure_descriptions.to_dict()

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

        base_document_markdown: Union[None, Unset, str]
        if isinstance(self.base_document_markdown, Unset):
            base_document_markdown = UNSET
        else:
            base_document_markdown = self.base_document_markdown

        content_processed: Union[None, Unset, str]
        if isinstance(self.content_processed, Unset):
            content_processed = UNSET
        else:
            content_processed = self.content_processed

        additional_info: Union[None, Unset, str]
        if isinstance(self.additional_info, Unset):
            additional_info = UNSET
        else:
            additional_info = self.additional_info

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "clasifier": clasifier,
                "structure": structure,
                "structure_descriptions": structure_descriptions,
            }
        )
        if base_document is not UNSET:
            field_dict["base_document"] = base_document
        if base_document_name is not UNSET:
            field_dict["base_document_name"] = base_document_name
        if base_document_markdown is not UNSET:
            field_dict["base_document_markdown"] = base_document_markdown
        if content_processed is not UNSET:
            field_dict["content_processed"] = content_processed
        if additional_info is not UNSET:
            field_dict["additional_info"] = additional_info
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_update_structure import ClientUpdateStructure
        from ..models.client_update_structure_descriptions import ClientUpdateStructureDescriptions

        d = dict(src_dict)
        name = d.pop("name")

        clasifier = d.pop("clasifier")

        structure = ClientUpdateStructure.from_dict(d.pop("structure"))

        structure_descriptions = ClientUpdateStructureDescriptions.from_dict(d.pop("structure_descriptions"))

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

        def _parse_base_document_markdown(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_document_markdown = _parse_base_document_markdown(d.pop("base_document_markdown", UNSET))

        def _parse_content_processed(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        content_processed = _parse_content_processed(d.pop("content_processed", UNSET))

        def _parse_additional_info(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        additional_info = _parse_additional_info(d.pop("additional_info", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        client_update = cls(
            name=name,
            clasifier=clasifier,
            structure=structure,
            structure_descriptions=structure_descriptions,
            base_document=base_document,
            base_document_name=base_document_name,
            base_document_markdown=base_document_markdown,
            content_processed=content_processed,
            additional_info=additional_info,
            created_at=created_at,
        )

        client_update.additional_properties = d
        return client_update

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
