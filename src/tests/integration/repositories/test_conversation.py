import random
from typing import Any

from deps_ai_fusion.domain.model.conversation import Conversation
from deps_ai_fusion.infrastructure.repositories import ConversationRepository


def test_saving__conversation__empty_conversation(
    conversation_repository: ConversationRepository,
    conversation: Conversation,
) -> None:
    conversation_repository.save(conversation)

    saved = conversation_repository.get(
        entity_id=conversation.entity_id(),
        tenant_id=conversation.tenant_id(),
        user_id=conversation.user_id(),
    )

    assert saved == conversation


def test_saving__conversation__with_completion(
    conversation_repository: ConversationRepository,
    conversation_with_completion: Conversation,
) -> None:
    conversation_repository.save(conversation_with_completion)

    saved = conversation_repository.get(
        entity_id=conversation_with_completion.entity_id(),
        tenant_id=conversation_with_completion.tenant_id(),
        user_id=conversation_with_completion.user_id(),
    )

    assert saved == conversation_with_completion
    assert saved.completions == conversation_with_completion.completions


def test__saving_same_conversation__no_error(
    conversation_repository: ConversationRepository,
    conversation_with_completion: Conversation,
) -> None:
    conversation_repository.save(conversation_with_completion)
    conversation_repository.save(conversation_with_completion)


def test__saving_incremental_completion__saved(
    conversation_repository: ConversationRepository,
    conversation: Conversation,
    raw_completion_data: dict[str, Any],
) -> None:
    conversation_repository.save(conversation)

    conversation.add_completion(
        provider=raw_completion_data["provider"],
        model=raw_completion_data["model"],
        question=raw_completion_data["question"],
        response=raw_completion_data["response"],
        confidence=raw_completion_data["confidence"],
    )

    conversation_repository.save(conversation)

    saved = conversation_repository.get(
        entity_id=conversation.entity_id(),
        tenant_id=conversation.tenant_id(),
        user_id=conversation.user_id(),
    )

    assert saved == conversation
    assert saved.completions == conversation.completions


def test_getting_multiple_completions__sorted_by_date(
    conversation_repository: ConversationRepository,
    conversation: Conversation,
    raw_completion_data: dict[str, Any],
) -> None:
    for i in range(10):
        conversation.add_completion(
            provider=raw_completion_data["provider"],
            model=raw_completion_data["model"],
            question=raw_completion_data["question"],
            response=raw_completion_data["response"],
            confidence=raw_completion_data["confidence"],
        )

    items = list(conversation.completions.items())
    random.shuffle(items)
    conversation.completions = dict(items)

    conversation_repository.save(conversation)

    saved = conversation_repository.get(
        entity_id=conversation.entity_id(),
        tenant_id=conversation.tenant_id(),
        user_id=conversation.user_id(),
    )

    assert list(saved.completions.values()) == sorted(
        list(conversation.completions.values()),
        key=lambda c: c.created_at,
    )


def test_getting__conversation__doesnt_exist__none(
    conversation_repository: ConversationRepository,
) -> None:
    assert (
        conversation_repository.get(
            entity_id="nonexistent_id",
            tenant_id="nonexistent_tenant",
            user_id="nonexistent_user",
        )
        is None
    )
