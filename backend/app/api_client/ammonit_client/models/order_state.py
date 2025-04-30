from enum import Enum


class OrderState(str, Enum):
    ERROR = "ERROR"
    INTEGRATED = "INTEGRATED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
