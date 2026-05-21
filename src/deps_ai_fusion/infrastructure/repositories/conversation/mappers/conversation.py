from typing import Any

from sqlalchemy import Row

from deps_ai_fusion.domain.model.conversation import Conversation

from .completion import CompletionMapper

__all__ = ["ConversationMapper"]


class ConversationMapper:
    @staticmethod
    def from_raw(raw_conversion: Row) -> Conversation:
        return Conversation(
            entity_id=raw_conversion.entity_id,
            user_id=raw_conversion.user_id,
            tenant_id=raw_conversion.tenant_id,
            completions=[
                CompletionMapper.from_dict(raw_completion) for raw_completion in raw_conversion.sorted_completions
            ],
        )

    @staticmethod
    def to_dict(conversation: Conversation) -> dict[str, Any]:
        return {
            "entity_id": conversation.entity_id(),
            "user_id": conversation.user_id(),
            "tenant_id": conversation.tenant_id(),
            "completions": [CompletionMapper.to_dict(completion) for completion in conversation.completions.values()],
        }
