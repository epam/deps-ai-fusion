from sqlalchemy import Column, String, Table, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB

from deps_ai_fusion.extras import metadata

__all__ = ["llm_extractor_table"]


llm_extractor_table = Table(
    "llm_extractor",
    metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, primary_key=True),
    Column("document_type_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("llm_reference", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    Column("queries", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    Column("extraction_params", JSONB, nullable=False),
    UniqueConstraint("name", "document_type_id", name="llm_extractor__name__document_type_id__ukey"),
)
