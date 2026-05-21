from deps_ai_fusion.domain.model.llm_extractor import (
    ILLMExtractorRepository,
    LLMExtractor,
    LLMExtractorsFilter,
)

__all__ = ["FakeLLMExtractorRepository"]


class FakeLLMExtractorRepository(ILLMExtractorRepository):
    def __init__(self) -> None:
        self._storage: dict[tuple[str, str], LLMExtractor] = {}

    def get(self, id_: str, tenant_id: str) -> LLMExtractor | None:
        return self._storage.get((id_, tenant_id))

    def find_all_for_document_type(self, document_type_id: str, tenant_id: str) -> list[LLMExtractor]:
        llm_extractors = []

        for extractor in self._storage.values():
            if extractor.document_type_id() == document_type_id and extractor.tenant_id() == tenant_id:
                llm_extractors.append(extractor)

        return llm_extractors

    def find_by_filter(self, filter_: LLMExtractorsFilter) -> list[LLMExtractor]:
        llm_extractors = []

        for extractor in self._storage.values():
            if filter_.ids is not None and extractor.id() not in filter_.ids:
                continue
            if filter_.tenant_id is not None and extractor.tenant_id() != filter_.tenant_id:
                continue
            if filter_.document_type_id is not None and extractor.document_type_id() != filter_.document_type_id:
                continue

            llm_extractors.append(extractor)

        return llm_extractors

    def find_for_document_type(self, id_: str, document_type_id: str, tenant_id: str) -> LLMExtractor | None:
        for extractor in self._storage.values():
            if (
                extractor.id() == id_
                and extractor.document_type_id() == document_type_id
                and extractor.tenant_id() == tenant_id
            ):
                return extractor

        return None

    def find_by_name_for_document_type(self, name: str, document_type_id: str, tenant_id: str) -> LLMExtractor | None:
        for extractor in self._storage.values():
            if (
                extractor.name == name
                and extractor.document_type_id() == document_type_id
                and extractor.tenant_id() == tenant_id
            ):
                return extractor

        return None

    def find_by_id(self, extractor_id: str, tenant_id: str) -> LLMExtractor | None:
        return self._storage.get(
            next(filter(lambda elem: elem == (extractor_id, tenant_id), self._storage.keys()), None)
        )

    def save(self, llm_extractor: LLMExtractor) -> None:
        self._storage[
            (
                llm_extractor.id(),
                llm_extractor.tenant_id(),
            )
        ] = llm_extractor

    def save_all(self, llm_extractors: list[LLMExtractor]) -> None:
        self.save_new_all(llm_extractors)

    def delete(self, extractor_id: str, tenant_id: str) -> None:
        self._storage.pop((extractor_id, tenant_id), None)

    def delete_for_document_type(self, document_type_id: str, tenant_id: str) -> None:
        keys_for_delete = []
        for key, value in self._storage.items():
            if value.document_type_id == document_type_id and value.tenant_id == tenant_id:
                keys_for_delete.append(key)
        for key in keys_for_delete:
            self._storage.pop(key)

    def save_new_all(self, extractors: list[LLMExtractor]) -> None:
        for el in extractors:
            if (el.id(), el.tenant_id()) in self._storage:
                continue
            else:
                self._storage[(el.id(), el.tenant_id())] = el
