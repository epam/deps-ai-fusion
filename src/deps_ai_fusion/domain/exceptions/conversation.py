from .base import BusinessError, NotFoundError

__all__ = ["ConversationNotFoundError", "CompletionLimitExceededError"]


class ConversationNotFoundError(NotFoundError):
    def __init__(self, entity_id: str, user_id: str, tenant_id: str) -> None:
        super().__init__(
            f"Conversation not found for {entity_id=}, {user_id=}, {tenant_id=}",
        )


class CompletionLimitExceededError(BusinessError):
    def __init__(self, entity_id: str, max_completions: int) -> None:
        super().__init__(
            f"Completion limit of {max_completions} exceeded for conversation {entity_id}",
        )
