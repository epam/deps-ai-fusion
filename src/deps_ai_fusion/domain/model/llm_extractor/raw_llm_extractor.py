from typing import TypedDict

from deps_gen_ai.providers import ProviderCode

from .raw_extraction_params import RawLLMExtractionParams

__all__ = ["RawLLMExtractor"]


class RawLLMExtractor(TypedDict):
    extractor_name: str
    provider: ProviderCode
    model: str
    extraction_params: RawLLMExtractionParams
    extractor_id: str | None
