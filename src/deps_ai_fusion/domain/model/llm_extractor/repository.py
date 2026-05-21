from typing import Protocol

from .filtering import LLMExtractorsFilter
from .llm_extractor import LLMExtractor

__all__ = ["ILLMExtractorRepository"]


class ILLMExtractorRepository(Protocol):
    def get(self, id_: str, tenant_id: str) -> LLMExtractor | None:
        ...

    def find_by_filter(self, filter_: LLMExtractorsFilter) -> list[LLMExtractor]:
        ...

    def find_for_document_type(self, id_: str, document_type_id: str, tenant_id: str) -> LLMExtractor | None:
        ...

    def find_by_name_for_document_type(self, name: str, document_type_id: str, tenant_id: str) -> LLMExtractor | None:
        ...

    def find_by_id(self, extractor_id: str, tenant_id: str) -> LLMExtractor | None:
        ...

    def save(self, llm_extractor: LLMExtractor) -> None:
        ...

    def save_all(self, llm_extractors: list[LLMExtractor]) -> None:
        ...

    def delete(self, extractor_id: str, tenant_id: str) -> None:
        ...

    def delete_for_document_type(self, document_type_id: str, tenant_id: str) -> None:
        ...
