from deps_ai_fusion.domain.model.conversation import Conversation

__all__ = ["ConversationFactory"]


class ConversationFactory:
    @classmethod
    def create(cls, entity_id: str, user_id: str, tenant_id: str) -> Conversation:
        return Conversation(
            entity_id=entity_id,
            user_id=user_id,
            tenant_id=tenant_id,
            completions=[],
        )
