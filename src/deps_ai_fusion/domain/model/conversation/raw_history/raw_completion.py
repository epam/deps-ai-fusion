from typing import TypedDict

__all__ = ["RawCompletion"]


class RawCompletion(TypedDict):
    question: str
    response: str
