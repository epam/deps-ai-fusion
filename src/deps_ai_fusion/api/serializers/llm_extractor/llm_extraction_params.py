from typing import Any

from pydantic import Field, model_validator

from deps_ai_fusion.domain.model import (
    DEFAULT_CUSTOM_INSTRUCTION,
    DEFAULT_GROUPING_FACTOR,
    DEFAULT_MAX_TOKENS,
    DEFAULT_SEED,
    DEFAULT_STOP,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    ContextAttachments,
    ExtractionParams,
)

from ..base import ConfiguredBaseModel

__all__ = ["SerializedLLMExtractionParams", "SerializedPageSpan"]


class SerializedPageSpan(ConfiguredBaseModel):
    start: int = Field(..., ge=1)
    end: int = Field(..., ge=1)

    @model_validator(mode="after")
    def check_order(self) -> "SerializedPageSpan":
        if self.start > self.end:
            raise ValueError("PageSpan.start must be less or equal to end")
        return self

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end}


class SerializedLLMExtractionParams(ConfiguredBaseModel):
    custom_instruction: str = Field(DEFAULT_CUSTOM_INSTRUCTION, alias="customInstruction")
    grouping_factor: int = Field(DEFAULT_GROUPING_FACTOR, alias="groupingFactor", ge=1)
    temperature: float = Field(DEFAULT_TEMPERATURE, ge=0, le=2)
    top_p: float = Field(DEFAULT_TOP_P, alias="topP", ge=0, le=1)
    max_tokens: int | None = Field(DEFAULT_MAX_TOKENS, alias="maxTokens", ge=1)
    stop: list[str] | None = Field(DEFAULT_STOP)
    seed: int | None = Field(DEFAULT_SEED)
    page_span: SerializedPageSpan | None = Field(None, alias="pageSpan")
    context_attachments: ContextAttachments | None = Field(None, alias="contextAttachments")

    @classmethod
    def from_model(cls, extraction_params: ExtractionParams) -> "SerializedLLMExtractionParams":
        return cls(
            custom_instruction=extraction_params.custom_instruction,
            grouping_factor=extraction_params.grouping_factor,
            temperature=extraction_params.temperature,
            top_p=extraction_params.top_p,
            max_tokens=extraction_params.max_tokens,
            stop=extraction_params.stop,
            seed=extraction_params.seed,
            page_span=SerializedPageSpan(**extraction_params.page_span.to_dict())
            if extraction_params.page_span
            else None,
            context_attachments=extraction_params.context_attachments,
        )
