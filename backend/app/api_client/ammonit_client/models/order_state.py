from enum import Enum


class OrderState(str, Enum):
    APPROVED = "APPROVED"
    INTEGRATED_ERROR = "INTEGRATED_ERROR"
    INTEGRATED_OK = "INTEGRATED_OK"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
