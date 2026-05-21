from typing import Any

from deps_ai_fusion.domain.model.conversation import (
    Conversation,
    IConversationRepository,
)

__all__ = ["FakeConversationRepository"]


class FakeConversationRepository(IConversationRepository):
    def __init__(self) -> None:
        self._storage: dict[tuple[str, str, str], Any] = {}

    def get(self, entity_id: str, user_id: str, tenant_id: str) -> Conversation | None:
        return self._storage.get((entity_id, user_id, tenant_id))

    def save(self, conversation: Any) -> None:
        self._storage[
            (
                conversation.entity_id(),
                conversation.user_id(),
                conversation.tenant_id(),
            )
        ] = conversation
