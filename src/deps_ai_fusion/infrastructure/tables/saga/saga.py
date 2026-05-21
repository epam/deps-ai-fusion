from sqlalchemy import Boolean, Column, String, Table

from deps_ai_fusion.extras import metadata

__all__ = ["saga_table"]


saga_table = Table(
    "saga",
    metadata,
    Column("saga_id", String, primary_key=True),
    Column("saga_type", String, nullable=False),
    Column("state_name", String, nullable=False),
    Column("last_request_id", String, nullable=False),
    Column("saga_data_type", String, nullable=False),
    Column("saga_data_json", String, nullable=False),
    Column("end_state", Boolean, nullable=False),
    Column("compensating", Boolean, nullable=False),
    Column("failed", Boolean, nullable=False),
)
