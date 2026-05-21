from deps_gen_ai.providers import ProviderCode
from pydantic import Field

from ..base import ConfiguredBaseModel

__all__ = ["AssignLLMToExtractorRequest", "AssignLLMToExtractorResponse"]


class AssignLLMToExtractorRequest(ConfiguredBaseModel):
    provider: ProviderCode
    model: str


class AssignLLMToExtractorResponse(ConfiguredBaseModel):
    extractor_id: str = Field(..., alias="extractorId")
    document_type_id: str = Field(..., alias="documentTypeId")
