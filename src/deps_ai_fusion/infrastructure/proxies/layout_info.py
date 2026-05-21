from typing import TypedDict

__all__ = ["RawLayoutInfo"]


class RawLayoutInfo(TypedDict):
    parsingFeatures: dict[str, list[str]]
