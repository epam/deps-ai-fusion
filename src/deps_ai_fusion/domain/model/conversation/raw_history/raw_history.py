from typing import TypedDict

from .raw_completion import RawCompletion

__all__ = ["RawConversationHistory"]


class RawConversationHistory(TypedDict):
    completions: list[RawCompletion]
