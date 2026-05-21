from sqlalchemy import Column, Select, and_, delete, select
from sqlalchemy.dialects.postgresql import insert

from deps_ai_fusion.domain.model.llm_extractor import (
    ILLMExtractorRepository,
    LLMExtractor,
    LLMExtractorsFilter,
)
from deps_ai_fusion.extras import Database

from ...tables import llm_extractor_table
from .mappers import LLMExtractorMapper

__all__ = ["LLMExtractorRepository"]


class LLMExtractorRepository(ILLMExtractorRepository):
    def __init__(self, db: Database) -> None:
        self._db = db

    @property
    def llm_extractor_columns(self) -> list[Column]:
        return [
            llm_extractor_table.c.id,
            llm_extractor_table.c.tenant_id,
            llm_extractor_table.c.document_type_id,
            llm_extractor_table.c.llm_reference,
            llm_extractor_table.c.name,
            llm_extractor_table.c.queries,
            llm_extractor_table.c.extraction_params,
        ]

    def get(self, id_: str, tenant_id: str) -> LLMExtractor | None:
        query = select(*self.llm_extractor_columns).where(
            and_(
                llm_extractor_table.c.id == id_,
                llm_extractor_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            row = conn.execute(query).fetchone()

        if not row:
            return None

        return LLMExtractorMapper.from_row(row)

    def find_by_filter(self, filter_: LLMExtractorsFilter) -> list[LLMExtractor]:
        query = self._filter_llm_extractors(filter_)

        with self._db.connection() as conn:
            rows = conn.execute(query).fetchall()

        return [LLMExtractorMapper.from_row(row) for row in rows]

    def find_for_document_type(self, id_: str, document_type_id: str, tenant_id: str) -> LLMExtractor | None:
        query = select(*self.llm_extractor_columns).where(
            and_(
                llm_extractor_table.c.id == id_,
                llm_extractor_table.c.document_type_id == document_type_id,
                llm_extractor_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            row = conn.execute(query).fetchone()

        if not row:
            return None

        return LLMExtractorMapper.from_row(row)

    def find_by_name_for_document_type(self, name: str, document_type_id: str, tenant_id: str) -> LLMExtractor | None:
        query = select(*self.llm_extractor_columns).where(
            and_(
                llm_extractor_table.c.name == name,
                llm_extractor_table.c.document_type_id == document_type_id,
                llm_extractor_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            row = conn.execute(query).fetchone()

        if not row:
            return None

        return LLMExtractorMapper.from_row(row)

    def find_by_id(self, extractor_id: str, tenant_id: str) -> LLMExtractor | None:
        query = select(*self.llm_extractor_columns).where(
            and_(llm_extractor_table.c.id == extractor_id, llm_extractor_table.c.tenant_id == tenant_id),
        )
        with self._db.connection() as conn:
            row = conn.execute(query).fetchone()

        return LLMExtractorMapper.from_row(row) if row else None

    def save(self, llm_extractor: LLMExtractor) -> None:
        raw_extractor = LLMExtractorMapper.to_dict(llm_extractor)

        insert_query = insert(llm_extractor_table).values(**raw_extractor)
        save_query = insert_query.on_conflict_do_update(
            index_elements=[llm_extractor_table.c.id, llm_extractor_table.c.tenant_id],
            set_={
                "llm_reference": insert_query.excluded.llm_reference,
                "name": insert_query.excluded.name,
                "queries": insert_query.excluded.queries,
                "extraction_params": insert_query.excluded.extraction_params,
            },
        )

        with self._db.connection() as conn:
            conn.execute(save_query)

    def save_all(self, llm_extractors: list[LLMExtractor]) -> None:
        save_queries = []
        for llm_extractor in llm_extractors:
            raw_extractor = LLMExtractorMapper.to_dict(llm_extractor)
            insert_query = insert(llm_extractor_table).values(**raw_extractor)
            save_query = insert_query.on_conflict_do_update(
                index_elements=[llm_extractor_table.c.id, llm_extractor_table.c.tenant_id],
                set_={
                    "llm_reference": insert_query.excluded.llm_reference,
                    "name": insert_query.excluded.name,
                    "queries": insert_query.excluded.queries,
                    "extraction_params": insert_query.excluded.extraction_params,
                },
            )
            save_queries.append(save_query)

        with self._db.connection() as conn:
            for save_query in save_queries:
                conn.execute(save_query)

    def delete(self, extractor_id: str, tenant_id: str) -> None:
        query = delete(llm_extractor_table).where(
            and_(llm_extractor_table.c.id == extractor_id, llm_extractor_table.c.tenant_id == tenant_id),
        )
        with self._db.connection() as conn:
            conn.execute(query)

    def delete_for_document_type(self, document_type_id: str, tenant_id: str) -> None:
        query = delete(llm_extractor_table).where(
            and_(
                llm_extractor_table.c.document_type_id == document_type_id,
                llm_extractor_table.c.tenant_id == tenant_id,
            ),
        )
        with self._db.connection() as conn:
            conn.execute(query)

    def _filter_llm_extractors(self, filter_: LLMExtractorsFilter) -> Select:
        query = select(*self.llm_extractor_columns)

        if filter_.ids is not None:
            query = query.where(llm_extractor_table.c.id.in_(filter_.ids))

        if filter_.tenant_id is not None:
            query = query.where(llm_extractor_table.c.tenant_id == filter_.tenant_id)

        if filter_.document_type_id is not None:
            query = query.where(llm_extractor_table.c.document_type_id == filter_.document_type_id)

        return query
