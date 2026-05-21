import uuid
from typing import Any

import pytest

from deps_ai_fusion.domain.events import LLMRequestLogged
from deps_ai_fusion.domain.exceptions import CompletionLimitExceededError
from deps_ai_fusion.domain.model.conversation import Completion, Conversation


def test_conversation__adding_completion(conversation: Conversation, raw_completion_data: dict[str, Any]) -> None:
    created_completion = conversation.add_completion(
        provider=raw_completion_data["provider"],
        model=raw_completion_data["model"],
        question=raw_completion_data["question"],
        response=raw_completion_data["response"],
        confidence=raw_completion_data["confidence"],
    )

    assert created_completion in conversation.completions.values()
    assert conversation.events == [
        LLMRequestLogged(
            entity_id=conversation.entity_id(),
            tenant_id=conversation.tenant_id(),
            user_id=conversation.user_id(),
            model=created_completion.llm_reference.model,
            provider=created_completion.llm_reference.provider,
            confidence=created_completion.confidence,
        ),
    ]


def test_conversation__completion_limit_exceeded__error(
    conversation: Conversation,
    raw_completion_data: dict[str, Any],
) -> None:
    for _ in range(100):
        conversation.add_completion(
            provider=raw_completion_data["provider"],
            model=raw_completion_data["model"],
            question=raw_completion_data["question"],
            response=raw_completion_data["response"],
            confidence=raw_completion_data["confidence"],
        )

    with pytest.raises(CompletionLimitExceededError):
        conversation.add_completion(
            provider=raw_completion_data["provider"],
            model=raw_completion_data["model"],
            question=raw_completion_data["question"],
            response=raw_completion_data["response"],
            confidence=raw_completion_data["confidence"],
        )


def test_conversation__removing_completions(
    conversation_with_completion: Conversation,
    test_completion: Completion,
) -> None:
    conversation_with_completion.remove_completions([test_completion.code, uuid.uuid4().hex])

    assert len(conversation_with_completion.completions) == 0


def test_conversation__forming_history(
    conversation_with_completion: Conversation,
    test_completion: Completion,
) -> None:
    assert conversation_with_completion.form_history() == {
        "completions": [
            {
                "question": test_completion.question,
                "response": test_completion.response,
            },
        ],
    }


def test_conversation__forming_history__limited(
    conversation: Conversation,
    raw_completion_data: dict[str, Any],
) -> None:
    conversation_completions = [
        conversation.add_completion(
            provider=raw_completion_data["provider"],
            model=raw_completion_data["model"],
            question=raw_completion_data["question"],
            response=raw_completion_data["response"],
            confidence=raw_completion_data["confidence"],
        )
        for _ in range(conversation._HISTORY_LIMIT)
    ]

    assert len(conversation.form_history()["completions"]) == conversation._HISTORY_LIMIT

    for completion, raw_completion in zip(
        conversation_completions[-conversation._HISTORY_LIMIT :],
        conversation.form_history()["completions"],
    ):
        assert raw_completion == {
            "question": completion.question,
            "response": completion.response,
        }


def test_conversation__clear(
    conversation_with_completion: Conversation,
) -> None:
    conversation_with_completion.clear()

    assert len(conversation_with_completion.completions) == 0
