import json
from typing import Literal

from deps_ai_fusion.application.types import RawAgentResponseChunk

from ..base import ConfiguredBaseModel

__all__ = ["AgentChunkResponse"]


class AgentChunkResponse(ConfiguredBaseModel):
    type: Literal["ToolCall", "Reasoning", "ToolCallResponse", "Final"]
    text: str

    @classmethod
    def json_from_chunk(cls, chunk: RawAgentResponseChunk) -> str:
        return json.dumps({"type": chunk["type_"], "text": chunk["text"]})
