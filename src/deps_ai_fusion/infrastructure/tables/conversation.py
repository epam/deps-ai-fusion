from sqlalchemy import Column, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_ai_fusion.extras.datasource import metadata

__all__ = ["conversation_table"]

conversation_table = Table(
    "conversation",
    metadata,
    Column("entity_id", String(), primary_key=True),
    Column("user_id", String(), primary_key=True),
    Column("tenant_id", String(), primary_key=True),
    Column("completions", JSONB),
)
