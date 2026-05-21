from enum import Enum

__all__ = ["ErrorType"]


class ErrorType(str, Enum):
    SYSTEM = "system"
    BUSINESS = "business"
