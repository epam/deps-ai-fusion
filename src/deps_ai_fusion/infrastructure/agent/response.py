import json
import logging
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from langchain_core.messages import AIMessage, ToolMessage

from deps_ai_fusion.application.types import RawAgentResponseChunk

__all__ = ["AgentChunk"]

_logger = logging.getLogger(__name__)

AnySupportedMessage: TypeAlias = AIMessage | ToolMessage


@dataclass
class AgentChunk:
    type_: Literal["ToolCall", "Reasoning", "ToolCallResponse", "Final"]
    text: str

    @classmethod
    def supports(cls, chunk: dict[str, Any]) -> bool:
        if "messages" not in chunk:
            return False

        last_msg = chunk["messages"][-1]

        return isinstance(last_msg, (AIMessage, ToolMessage))

    @classmethod
    def from_langchain_message(cls, msg: AnySupportedMessage) -> "AgentChunk":
        if isinstance(msg, AIMessage) and msg.additional_kwargs.get("tool_calls"):
            call = msg.additional_kwargs["tool_calls"][0]["function"]

            try:
                arguments = json.loads(call["arguments"]).get("reasoning", "no reasoning provided")
            except json.JSONDecodeError:
                arguments = call["arguments"]

            return cls(type_="ToolCall", text=f"I have to call '{call['name']}', {arguments}.")
        elif isinstance(msg, AIMessage):
            return cls(type_="Final", text=str(msg.content))
        elif isinstance(msg, ToolMessage):
            if msg.status == "error":
                _logger.error(f"Tool `{msg.name}` responded with error: `{msg.content}`")

            return cls(type_="ToolCallResponse", text=f"Tool {msg.name} responded with {msg.status}.")

        raise RuntimeError(f"Unsupported message type: {type(msg)}")

    def to_raw(self) -> RawAgentResponseChunk:
        return {
            "type_": self.type_,
            "text": self.text,
        }
