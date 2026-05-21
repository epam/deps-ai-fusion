from sqlalchemy import Column, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_ai_fusion.extras.datasource import metadata

__all__ = ["insights_table"]

insights_table = Table(
    "insights",
    metadata,
    Column("conversation_id", String(), primary_key=True),
    Column("tenant_id", String(), primary_key=True),
    Column("insights", JSONB, nullable=False),
)
