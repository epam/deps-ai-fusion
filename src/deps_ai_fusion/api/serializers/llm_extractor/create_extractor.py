from typing import Any

from deps_gen_ai.providers import ProviderCode
from pydantic import Field

from deps_ai_fusion.domain.model import RawLLMExtractionParams, RawLLMExtractor

from ..base import ConfiguredBaseModel
from .llm_extraction_params import SerializedLLMExtractionParams

__all__ = ["CreateExtractorRequest", "CreateExtractorResponse"]


class CreateExtractorRequest(ConfiguredBaseModel):
    extractor_name: str = Field(..., alias="extractorName")
    provider: ProviderCode
    model: str
    document_type_name: str = Field(..., alias="documentTypeName")
    extractor_id: str | None = Field(default=None, alias="extractorId")

    extraction_params: SerializedLLMExtractionParams = Field(..., alias="extractionParams")

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_type_name": self.document_type_name,
            "extractor": RawLLMExtractor(
                extractor_name=self.extractor_name,
                provider=self.provider,
                model=self.model,
                extractor_id=self.extractor_id,
                extraction_params=RawLLMExtractionParams(
                    custom_instruction=self.extraction_params.custom_instruction,
                    grouping_factor=self.extraction_params.grouping_factor,
                    temperature=self.extraction_params.temperature,
                    top_p=self.extraction_params.top_p,
                    page_span=self.extraction_params.page_span.to_dict() if self.extraction_params.page_span else None,
                    context_attachments=self.extraction_params.context_attachments,
                ),
            ),
        }


class CreateExtractorResponse(ConfiguredBaseModel):
    extractor_id: str = Field(..., alias="extractorId")
    document_type_id: str = Field(..., alias="documentTypeId")
