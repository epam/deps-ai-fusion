from typing import Any

from deps_gen_ai.common import LLMResponse, RetrievedInsights
from pydantic import Field

from deps_ai_fusion.api.serializers.base import ConfiguredBaseModel
from deps_ai_fusion.application.structured_outputs import ReasoningResponse

__all__ = ["SerializedRetrievedInsights"]


class Insight(ConfiguredBaseModel):
    content: str
    error_occurred: bool = Field(..., alias="errorOccurred")
    confidence: float | None

    @classmethod
    def from_llm_response(cls, response: LLMResponse[ReasoningResponse | dict[str, Any]]) -> "Insight":
        return cls(
            content=ReasoningResponse.parse_llm_response(response),
            confidence=response.confidence,
            error_occurred=not response.success,
        )


class SerializedRetrievedInsights(ConfiguredBaseModel):
    elements: dict[str, Insight]

    @classmethod
    def from_model(cls, model: RetrievedInsights) -> "SerializedRetrievedInsights":
        return cls(
            elements={code: Insight.from_llm_response(llm_response) for code, llm_response in model.insights.items()},
        )
