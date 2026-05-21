from typing import TypedDict

from .extraction_params.context_attachments import ContextAttachments

__all__ = ["RawLLMExtractionParams", "RawPageSpan"]


class RawPageSpan(TypedDict):
    start: int
    end: int


class RawLLMExtractionParams(TypedDict):
    custom_instruction: str
    grouping_factor: int
    temperature: float
    top_p: float
    page_span: RawPageSpan | None
    context_attachments: ContextAttachments | None
