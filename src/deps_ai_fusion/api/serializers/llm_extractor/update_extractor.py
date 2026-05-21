from pydantic import Field

from deps_ai_fusion.domain.model import ContextAttachments

from ..base import ConfiguredBaseModel
from .llm_extraction_params import SerializedPageSpan

__all__ = ["UpdateExtractorRequest", "UpdateExtractorResponse"]


class UpdateExtractorParams(ConfiguredBaseModel):
    custom_instruction: str = Field(..., alias="customInstruction")
    grouping_factor: int = Field(..., ge=1, alias="groupingFactor")
    temperature: float = Field(..., ge=0, le=2)
    top_p: float = Field(..., ge=0, le=1, alias="topP")
    page_span: SerializedPageSpan | None = Field(..., alias="pageSpan")
    context_attachments: ContextAttachments | None = Field(None, alias="contextAttachments")


class UpdateExtractorRequest(ConfiguredBaseModel):
    name: str
    extraction_params: UpdateExtractorParams = Field(..., alias="extractionParams")


class UpdateExtractorResponse(ConfiguredBaseModel):
    extractor_id: str = Field(..., alias="extractorId")
    document_type_id: str = Field(..., alias="documentTypeId")
