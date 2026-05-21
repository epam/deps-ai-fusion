from sqlalchemy import Column, ForeignKey, String, Table

from deps_ai_fusion.extras import metadata

__all__ = ["entity_saga_pair_table"]


entity_saga_pair_table = Table(
    "entity_saga_pair",
    metadata,
    Column("entity_id", String, primary_key=True),
    Column(
        "saga_id",
        String,
        ForeignKey("saga.saga_id", onupdate="cascade", ondelete="cascade"),
        nullable=False,
    ),
)
