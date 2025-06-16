import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prompt_update_structure_type_0 import PromptUpdateStructureType0


T = TypeVar("T", bound="PromptUpdate")


@_attrs_define
class PromptUpdate:
    """
    Attributes:
        query (Union[None, Unset, str]):
        service (Union[None, Unset, str]):
        model (Union[None, Unset, str]):
        prompt (Union[None, Unset, str]):
        structure (Union['PromptUpdateStructureType0', None, Unset]):
        version (Union[Unset, int]):  Default: 1.
        created_at (Union[Unset, datetime.datetime]):
    """

    query: Union[None, Unset, str] = UNSET
    service: Union[None, Unset, str] = UNSET
    model: Union[None, Unset, str] = UNSET
    prompt: Union[None, Unset, str] = UNSET
    structure: Union["PromptUpdateStructureType0", None, Unset] = UNSET
    version: Union[Unset, int] = 1
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prompt_update_structure_type_0 import PromptUpdateStructureType0

        query: Union[None, Unset, str]
        if isinstance(self.query, Unset):
            query = UNSET
        else:
            query = self.query

        service: Union[None, Unset, str]
        if isinstance(self.service, Unset):
            service = UNSET
        else:
            service = self.service

        model: Union[None, Unset, str]
        if isinstance(self.model, Unset):
            model = UNSET
        else:
            model = self.model

        prompt: Union[None, Unset, str]
        if isinstance(self.prompt, Unset):
            prompt = UNSET
        else:
            prompt = self.prompt

        structure: Union[None, Unset, dict[str, Any]]
        if isinstance(self.structure, Unset):
            structure = UNSET
        elif isinstance(self.structure, PromptUpdateStructureType0):
            structure = self.structure.to_dict()
        else:
            structure = self.structure

        version = self.version

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if query is not UNSET:
            field_dict["query"] = query
        if service is not UNSET:
            field_dict["service"] = service
        if model is not UNSET:
            field_dict["model"] = model
        if prompt is not UNSET:
            field_dict["prompt"] = prompt
        if structure is not UNSET:
            field_dict["structure"] = structure
        if version is not UNSET:
            field_dict["version"] = version
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_update_structure_type_0 import PromptUpdateStructureType0

        d = dict(src_dict)

        def _parse_query(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        query = _parse_query(d.pop("query", UNSET))

        def _parse_service(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service = _parse_service(d.pop("service", UNSET))

        def _parse_model(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        model = _parse_model(d.pop("model", UNSET))

        def _parse_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        prompt = _parse_prompt(d.pop("prompt", UNSET))

        def _parse_structure(data: object) -> Union["PromptUpdateStructureType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                structure_type_0 = PromptUpdateStructureType0.from_dict(data)

                return structure_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptUpdateStructureType0", None, Unset], data)

        structure = _parse_structure(d.pop("structure", UNSET))

        version = d.pop("version", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        prompt_update = cls(
            query=query,
            service=service,
            model=model,
            prompt=prompt,
            structure=structure,
            version=version,
            created_at=created_at,
        )

        prompt_update.additional_properties = d
        return prompt_update

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
