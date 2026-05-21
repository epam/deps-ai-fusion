from sqlalchemy import CursorResult

from deps_ai_fusion.domain.model.conversation import (
    Conversation,
    IConversationRepository,
)
from deps_ai_fusion.extras import Database

from .mappers import ConversationMapper
from .query_factory import ConversationQueryFactory

__all__ = ["ConversationRepository"]


class ConversationRepository(IConversationRepository):
    def __init__(self, db: Database) -> None:
        self._db = db
        self._queries = ConversationQueryFactory()

    def get(self, entity_id: str, user_id: str, tenant_id: str) -> Conversation | None:
        with self._db.connection() as conn:
            conversation_row: CursorResult = conn.execute(
                self._queries.select_conversation(
                    entity_id=entity_id,
                    user_id=user_id,
                    tenant_id=tenant_id,
                ),
            )

            if not conversation_row.rowcount:
                return None

        return ConversationMapper.from_raw(raw_conversion=conversation_row.first())

    def save(self, conversation: Conversation) -> None:
        raw_conversation = ConversationMapper.to_dict(conversation)

        with self._db.connection() as conn:
            conn.execute(self._queries.insert_conversation().values(**raw_conversation))
