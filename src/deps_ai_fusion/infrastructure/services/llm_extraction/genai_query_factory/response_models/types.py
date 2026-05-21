from typing import TypedDict

__all__ = [
    "RawKeyValuePair",
    "RawKeyValuePairWithAlias",
    "BooleanWithAlias",
    "StringWithAlias",
]


class RawKeyValuePair(TypedDict):
    key: str
    value: str


class RawKeyValuePairWithAlias(RawKeyValuePair):
    alias: str


class BooleanWithAlias(TypedDict):
    value: bool | None
    alias: str


class StringWithAlias(TypedDict):
    value: str
    alias: str
