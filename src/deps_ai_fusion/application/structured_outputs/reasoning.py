import json

from deps_gen_ai.common import LLMResponse
from pydantic import BaseModel, Field

__all__ = ["ReasoningResponse"]

_FINAL_RESPONSE_KEYS = ("final_response", "Final Response")


class ReasoningResponse(BaseModel):
    reasoning: str = Field(
        ...,
        title="reasoning",
        description="Detailed, step-by-step reasoning process leading to the final response.",
    )
    final_response: str = Field(
        ...,
        title="final_response",
        description="The final answer or result derived from the reasoning process.",
    )

    @classmethod
    def parse_llm_response(cls, response: LLMResponse) -> str:
        if response.parsed and isinstance(response.parsed, ReasoningResponse):
            return response.parsed.final_response
        if response.parsed and isinstance(response.parsed, dict):
            for key in _FINAL_RESPONSE_KEYS:
                if key in response.parsed:
                    return response.parsed[key]

            return json.dumps(response.parsed, indent=2, ensure_ascii=False)

        return response.content
