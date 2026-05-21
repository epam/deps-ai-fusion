from enum import Enum

__all__ = ["DataType"]


class DataType(str, Enum):
    STRING = "String"
    BOOLEAN = "Boolean"
    KEY_VALUE_PAIR = "KeyValuePair"
