from typing import Any, Literal, TypeAlias, TypedDict

__all__ = [
    "RawAgentArgument",
    "RawConversationTurn",
    "RawContextBundle",
    "RawAgentArguments",
    "RawAgentResponseChunk",
]


class RawAgentResponseChunk(TypedDict):
    type_: Literal["ToolCall", "Reasoning", "ToolCallResponse", "Final"]
    text: str


class RawAgentArgument(TypedDict):
    value: Any


class RawConversationTurn(TypedDict):
    question: str
    answer: str


class RawContextBundle(TypedDict):
    conversation_trim: list[RawConversationTurn]


ToolDataCode: TypeAlias = str
RawAgentArguments: TypeAlias = dict[ToolDataCode, list[RawAgentArgument]]
