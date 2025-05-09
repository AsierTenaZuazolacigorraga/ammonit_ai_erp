from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.email_create import EmailCreate
    from ..models.outlook_token_step_2 import OutlookTokenStep2


T = TypeVar("T", bound="BodyEmailsCreateOutlookTokenStep2")


@_attrs_define
class BodyEmailsCreateOutlookTokenStep2:
    """
    Attributes:
        data (OutlookTokenStep2):
        email_in (EmailCreate):
    """

    data: "OutlookTokenStep2"
    email_in: "EmailCreate"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        email_in = self.email_in.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "email_in": email_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_create import EmailCreate
        from ..models.outlook_token_step_2 import OutlookTokenStep2

        d = dict(src_dict)
        data = OutlookTokenStep2.from_dict(d.pop("data"))

        email_in = EmailCreate.from_dict(d.pop("email_in"))

        body_emails_create_outlook_token_step_2 = cls(
            data=data,
            email_in=email_in,
        )

        body_emails_create_outlook_token_step_2.additional_properties = d
        return body_emails_create_outlook_token_step_2

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
