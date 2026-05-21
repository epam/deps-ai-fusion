from sqlalchemy import CursorResult, and_, delete, select
from sqlalchemy.dialects.postgresql import insert

from deps_ai_fusion.application import IInsightsStore
from deps_ai_fusion.extras import Database
from deps_ai_fusion.infrastructure.tables.insights import insights_table

__all__ = ["InsightsRepository"]


class InsightsRepository(IInsightsStore):
    def __init__(self, db: Database) -> None:
        self._db = db

    def load(self, conversation_id: str, tenant_id: str) -> list[str]:
        with self._db.connection() as conn:
            result: CursorResult = conn.execute(
                select(insights_table.c.insights).where(
                    and_(
                        insights_table.c.conversation_id == conversation_id,
                        insights_table.c.tenant_id == tenant_id,
                    )
                )
            )

            if (row := result.first()) is None:
                return []

            return row.insights or []

    def save(self, conversation_id: str, tenant_id: str, insights: list[str]) -> None:
        with self._db.connection() as conn:
            query = insert(insights_table).values(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                insights=insights,
            )

            query = query.on_conflict_do_update(
                index_elements=[insights_table.c.conversation_id, insights_table.c.tenant_id],
                set_={"insights": query.excluded.insights},
            )

            conn.execute(query)

    def delete_by_conversation_id(self, conversation_id: str) -> None:
        with self._db.connection() as conn:
            query = delete(insights_table).where(insights_table.c.conversation_id == conversation_id)
            conn.execute(query)
