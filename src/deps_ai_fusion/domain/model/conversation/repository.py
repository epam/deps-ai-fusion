from typing import Protocol

from .conversation import Conversation

__all__ = ["IConversationRepository"]


class IConversationRepository(Protocol):
    def get(self, entity_id: str, user_id: str, tenant_id: str) -> Conversation | None:
        ...

    def save(self, conversation: Conversation) -> None:
        ...
