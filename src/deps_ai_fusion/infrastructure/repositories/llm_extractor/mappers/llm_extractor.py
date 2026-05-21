from typing import Any

from sqlalchemy import Row

from deps_ai_fusion.domain.model import LLMExtractor, LLMReference

from .extraction_params import ExtractionParamsMapper
from .query import QueryMapper

__all__ = ["LLMExtractorMapper"]


class LLMExtractorMapper:
    @staticmethod
    def from_row(llm_extractor_row: Row) -> LLMExtractor:
        return LLMExtractor(
            id_=llm_extractor_row.id,
            tenant_id=llm_extractor_row.tenant_id,
            document_type_id=llm_extractor_row.document_type_id,
            name=llm_extractor_row.name,
            llm_reference=LLMReference(
                provider=llm_extractor_row.llm_reference["provider"],
                model=llm_extractor_row.llm_reference["model"],
            ),
            queries={code: QueryMapper.from_dict(query) for code, query in llm_extractor_row.queries.items()},
            extraction_params=ExtractionParamsMapper.from_dict(llm_extractor_row.extraction_params),
        )

    @staticmethod
    def to_dict(llm_extractor: LLMExtractor) -> dict[str, Any]:
        return {
            "id": llm_extractor.id(),
            "tenant_id": llm_extractor.tenant_id(),
            "document_type_id": llm_extractor.document_type_id(),
            "name": llm_extractor.name,
            "llm_reference": {
                "provider": llm_extractor.llm_reference.provider,
                "model": llm_extractor.llm_reference.model,
            },
            "queries": {code: QueryMapper.to_dict(query) for code, query in llm_extractor.queries.items()},
            "extraction_params": ExtractionParamsMapper.to_dict(llm_extractor.extraction_params),
        }
