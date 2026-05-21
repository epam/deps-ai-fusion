from deps_gen_ai.providers import ProviderCode
from pydantic import Field

from deps_ai_fusion.domain.model import LLMExtractor

from ..base import ConfiguredBaseModel
from .llm_extraction_params import SerializedLLMExtractionParams
from .query import SerializedQuery

__all__ = ["SerializedLLMExtractor"]


class SerializedLLMReference(ConfiguredBaseModel):
    provider: ProviderCode
    model: str


class SerializedLLMExtractor(ConfiguredBaseModel):
    extractor_id: str = Field(..., alias="extractorId")
    name: str
    llm_reference: SerializedLLMReference = Field(..., alias="llmReference")
    queries: list[SerializedQuery]

    extraction_params: SerializedLLMExtractionParams = Field(..., alias="extractionParams")

    @classmethod
    def from_model(cls, llm_extractor: LLMExtractor) -> "SerializedLLMExtractor":
        return cls(
            extractor_id=llm_extractor.id(),
            name=llm_extractor.name,
            llm_reference=SerializedLLMReference(
                provider=llm_extractor.llm_reference.provider,
                model=llm_extractor.llm_reference.model,
            ),
            extraction_params=SerializedLLMExtractionParams.from_model(
                extraction_params=llm_extractor.extraction_params,
            ),
            queries=[SerializedQuery.from_model(query) for query in llm_extractor.query_values()],
        )
