from typing import TypedDict

__all__ = ["RawPageSpan"]


class RawPageSpan(TypedDict):
    start: int
    end: int
