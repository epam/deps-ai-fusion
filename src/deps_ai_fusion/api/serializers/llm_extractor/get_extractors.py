from pydantic import Field

from deps_ai_fusion.domain.model import LLMExtractor

from ..base import ConfiguredBaseModel
from .extractor import SerializedLLMExtractor

__all__ = ["GetLLMExtractorsResponse"]


class GetLLMExtractorsResponse(ConfiguredBaseModel):
    llm_extractors: list[SerializedLLMExtractor] = Field(..., alias="llmExtractors")

    @classmethod
    def from_list(cls, llm_extractors: list[LLMExtractor]) -> "GetLLMExtractorsResponse":
        return cls(
            llm_extractors=[SerializedLLMExtractor.from_model(llm_extractor) for llm_extractor in llm_extractors],
        )
