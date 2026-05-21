import uuid

import pytest
from deps_gen_ai.providers import ProviderCode

from deps_ai_fusion.application import ConversationService
from deps_ai_fusion.application.types import RawPageSpan
from deps_ai_fusion.domain.events import LLMRequestLogged
from deps_ai_fusion.domain.exceptions import ConversationNotFoundError
from deps_ai_fusion.domain.model.conversation import Completion, Conversation
from tests.fakes import (
    FakeConversationRepository,
    FakeEventPublisher,
    FakeProvidersAggregate,
)


def test_chat_request__completion_saved__event_published(
    fake_conversation_repository: FakeConversationRepository,
    fake_event_publisher: FakeEventPublisher,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
    conversation: Conversation,
    raw_completion_data: dict[str, str],
) -> None:
    fake_conversation_repository.save(conversation)
    fake_providers_aggregate.set_response(raw_completion_data["response"])

    completion = conversation_service.chat_request(
        entity_id=conversation.entity_id(),
        tenant_id=conversation.tenant_id(),
        user_id=conversation.user_id(),
        provider=raw_completion_data["provider"],
        model=raw_completion_data["model"],
        question=raw_completion_data["question"],
    )

    saved_conversation = fake_conversation_repository.get(
        conversation.entity_id(),
        conversation.user_id(),
        conversation.tenant_id(),
    )

    assert saved_conversation is not None
    assert len(saved_conversation.completions) == 1
    assert completion == list(saved_conversation.completions.values())[0]
    assert fake_event_publisher.published_events == [
        LLMRequestLogged(
            entity_id=conversation.entity_id(),
            tenant_id=conversation.tenant_id(),
            user_id=conversation.user_id(),
            provider=raw_completion_data["provider"],
            model=raw_completion_data["model"],
        ),
    ]


def test_chat_request_with_page_span__no_error(
    fake_conversation_repository: FakeConversationRepository,
    fake_event_publisher: FakeEventPublisher,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
    conversation: Conversation,
    raw_completion_data: dict[str, str],
) -> None:
    fake_conversation_repository.save(conversation)
    fake_providers_aggregate.set_response(raw_completion_data["response"])

    conversation_service.chat_request(
        entity_id=conversation.entity_id(),
        tenant_id=conversation.tenant_id(),
        user_id=conversation.user_id(),
        provider=raw_completion_data["provider"],
        model=raw_completion_data["model"],
        question=raw_completion_data["question"],
        page_span=RawPageSpan(start=1, end=5),
    )


def test_chat_request_with_files__no_error(
    fake_conversation_repository: FakeConversationRepository,
    fake_event_publisher: FakeEventPublisher,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
    conversation: Conversation,
    raw_completion_data: dict[str, str],
) -> None:
    fake_conversation_repository.save(conversation)
    fake_providers_aggregate.set_response(raw_completion_data["response"])

    conversation_service.chat_request(
        entity_id=conversation.entity_id(),
        tenant_id=conversation.tenant_id(),
        user_id=conversation.user_id(),
        provider=raw_completion_data["provider"],
        model=raw_completion_data["model"],
        question=raw_completion_data["question"],
        files=["file1.png", "file2.png"],
    )


def test_chat_request__conversation_not_found__error_raised(
    fake_conversation_repository: FakeConversationRepository,
    conversation_service: ConversationService,
    raw_completion_data: dict[str, str],
) -> None:
    with pytest.raises(ConversationNotFoundError):
        conversation_service.chat_request(
            entity_id="unknown_entity_id",
            tenant_id="unknown_tenant_id",
            user_id="unknown_user_id",
            provider=raw_completion_data["provider"],
            model=raw_completion_data["model"],
            question=raw_completion_data["question"],
        )


def test_clear_conversation__cleared(
    fake_conversation_repository: FakeConversationRepository,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_with_completion: Conversation,
    conversation_service: ConversationService,
) -> None:
    fake_conversation_repository.save(conversation_with_completion)

    conversation_service.clear_conversation(
        entity_id=conversation_with_completion.entity_id(),
        tenant_id=conversation_with_completion.tenant_id(),
        user_id=conversation_with_completion.user_id(),
    )

    saved_conversation = fake_conversation_repository.get(
        conversation_with_completion.entity_id(),
        conversation_with_completion.user_id(),
        conversation_with_completion.tenant_id(),
    )
    assert len(saved_conversation.completions) == 0


def test_clear_conversation__not_found__error_raised(
    fake_conversation_repository: FakeConversationRepository,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
) -> None:
    with pytest.raises(ConversationNotFoundError):
        conversation_service.clear_conversation(
            entity_id="unknown_entity_id", tenant_id="unknown_tenant_id", user_id="unknown_user_id"
        )


def test_remove_completions__deleted(
    conversation_with_completion: Conversation,
    test_completion: Completion,
    fake_conversation_repository: FakeConversationRepository,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
) -> None:
    fake_conversation_repository.save(conversation_with_completion)

    conversation_service.remove_completions(
        entity_id=conversation_with_completion.entity_id(),
        tenant_id=conversation_with_completion.tenant_id(),
        user_id=conversation_with_completion.user_id(),
        completion_codes=[test_completion.code, uuid.uuid4().hex],
    )

    saved_conversation = fake_conversation_repository.get(
        conversation_with_completion.entity_id(),
        conversation_with_completion.user_id(),
        conversation_with_completion.tenant_id(),
    )
    assert len(saved_conversation.completions) == 0


def test_remove_completions__conversation_does_not_exist__error(
    fake_conversation_repository: FakeConversationRepository,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
) -> None:
    with pytest.raises(ConversationNotFoundError):
        conversation_service.remove_completions(
            entity_id=uuid.uuid4().hex,
            tenant_id=uuid.uuid4().hex,
            user_id=uuid.uuid4().hex,
            completion_codes=[uuid.uuid4().hex],
        )


def test_get_conversation__conversation_not_found__created(
    fake_conversation_repository: FakeConversationRepository,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
) -> None:
    conversation_info = conversation_service.get_conversation(
        entity_id="unknown_entity_id",
        tenant_id="unknown_tenant_id",
        user_id="unknown_user_id",
    )

    assert conversation_info is not None

    conversation = conversation_info.conversation
    assert fake_conversation_repository.get(
        conversation.entity_id(),
        conversation.user_id(),
        conversation.tenant_id(),
    )


def test_get_conversation__conversation_exists__returned(
    fake_conversation_repository: FakeConversationRepository,
    fake_providers_aggregate: FakeProvidersAggregate,
    conversation_service: ConversationService,
    conversation_with_completion: Conversation,
) -> None:
    fake_conversation_repository.save(conversation_with_completion)

    conversation_info = conversation_service.get_conversation(
        entity_id=conversation_with_completion.entity_id(),
        tenant_id=conversation_with_completion.tenant_id(),
        user_id=conversation_with_completion.user_id(),
    )

    assert conversation_info is not None

    assert conversation_info.conversation == conversation_with_completion
    assert conversation_info.providers == fake_providers_aggregate.providers

    for provider in conversation_info.providers:
        assert conversation_info.models[ProviderCode(provider.code)] == fake_providers_aggregate.models_of(
            provider=provider.code, include_legacy=False
        )
