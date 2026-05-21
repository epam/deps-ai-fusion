from typing import Any

from deps_ai_fusion.domain.model.llm_extractor import (
    ContextAttachments,
    ExtractionParams,
    PageSpan,
)

__all__ = ["ExtractionParamsMapper"]


class ExtractionParamsMapper:
    @staticmethod
    def from_dict(raw_extraction_params: dict[str, Any]) -> ExtractionParams:
        page_span = raw_extraction_params.get("page_span")
        context_attachments = raw_extraction_params.get("context_attachments")
        return ExtractionParams(
            custom_instruction=raw_extraction_params.get("custom_instruction"),
            grouping_factor=raw_extraction_params.get("grouping_factor"),
            temperature=raw_extraction_params.get("temperature"),
            top_p=raw_extraction_params.get("top_p"),
            max_tokens=raw_extraction_params.get("max_tokens"),
            stop=raw_extraction_params.get("stop"),
            seed=raw_extraction_params.get("seed"),
            page_span=PageSpan.from_dict(page_span) if page_span else None,
            context_attachments=ContextAttachments(context_attachments) if context_attachments else None,
        )

    @staticmethod
    def to_dict(extraction_params: ExtractionParams) -> dict[str, Any]:
        return {
            "custom_instruction": extraction_params.custom_instruction,
            "grouping_factor": extraction_params.grouping_factor,
            "temperature": extraction_params.temperature,
            "top_p": extraction_params.top_p,
            "max_tokens": extraction_params.max_tokens,
            "stop": extraction_params.stop,
            "seed": extraction_params.seed,
            "page_span": extraction_params.page_span.to_dict() if extraction_params.page_span else None,
            "context_attachments": extraction_params.context_attachments.value
            if extraction_params.context_attachments
            else None,
        }
