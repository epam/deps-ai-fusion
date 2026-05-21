from uuid import uuid4

from deps_gen_ai.providers import ProviderCode

from ..shared import LLMReference
from .extraction_params import ExtractionParams, PageSpan
from .llm_extractor import LLMExtractor
from .raw_extraction_params import RawLLMExtractionParams

__all__ = ["LLMExtractorFactory"]


class LLMExtractorFactory:
    @classmethod
    def create(
        cls,
        tenant_id: str,
        document_type_id: str,
        provider: ProviderCode,
        name: str,
        model: str,
        id_: str | None = None,
        extraction_params: RawLLMExtractionParams | None = None,
    ) -> LLMExtractor:
        return LLMExtractor(
            id_=id_ if id_ is not None else uuid4().hex,
            tenant_id=tenant_id,
            document_type_id=document_type_id,
            name=name,
            llm_reference=LLMReference(provider=provider, model=model),
            queries={},
            extraction_params=cls._create_extraction_params_from(extraction_params),
        )

    @staticmethod
    def _create_extraction_params_from(extraction_params: RawLLMExtractionParams | None) -> ExtractionParams:
        if extraction_params:
            return ExtractionParams(
                custom_instruction=extraction_params["custom_instruction"],
                grouping_factor=extraction_params["grouping_factor"],
                temperature=extraction_params["temperature"],
                top_p=extraction_params["top_p"],
                page_span=PageSpan.from_dict(extraction_params["page_span"])
                if extraction_params["page_span"]
                else None,
                context_attachments=extraction_params["context_attachments"],
            )

        return ExtractionParams()
