from datetime import datetime

from pydantic import Field

from deps_ai_fusion.domain.model.conversation import Completion

from ..base import ConfiguredBaseModel
from ..llm_extractor import SerializedPageSpan

__all__ = ["SerializedCompletion", "CreateCompletionRequest"]


class CreateCompletionRequest(ConfiguredBaseModel):
    question: str
    model: str
    provider: str
    page_span: SerializedPageSpan | None = Field(default=None, alias="pageSpan")
    files: list[str] | None = None


class SerializedCompletion(ConfiguredBaseModel):
    code: str
    question: str
    response: str
    model: str
    provider: str
    confidence: float | None
    created_at: datetime = Field(..., alias="createdAt")

    @classmethod
    def from_domain(cls, completion: Completion) -> "SerializedCompletion":
        return cls(
            code=completion.code,
            question=completion.question,
            response=completion.response,
            model=completion.llm_reference.model,
            provider=completion.llm_reference.provider,
            confidence=completion.confidence,
            created_at=completion.created_at,
        )
