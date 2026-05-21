import uuid

from fastapi import status
from fastapi.testclient import TestClient

from deps_ai_fusion.constants import V1_API_PREFIX
from deps_ai_fusion.domain.model.conversation import Completion, Conversation
from tests.factories import test_user_data
from tests.fakes import FakeConversationRepository, FakeProvidersAggregate

_FIRST_ELEMENT: int = 0


class TestConversation:
    endpoint = V1_API_PREFIX + "/conversations"

    def test_creating_completion__conversation_not_exists__404(
        self,
        fake_conversation_repository,
        fake_providers_aggregate: FakeProvidersAggregate,
        authenticated_client: TestClient,
        raw_create_completion_request: dict[str, str],
    ) -> None:
        response = authenticated_client.put(
            f"{self.endpoint}/random-entity-id",
            json=raw_create_completion_request,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_creating_completion__valid_response(
        self,
        conversation: Conversation,
        fake_conversation_repository: FakeConversationRepository,
        fake_providers_aggregate: FakeProvidersAggregate,
        fake_event_publisher,
        authenticated_client: TestClient,
        raw_create_completion_request: dict[str, str],
    ) -> None:
        fake_conversation_repository.save(conversation)

        fake_llm_response, fake_confidence = "something", 0.25
        fake_providers_aggregate.set_response(response=fake_llm_response, confidence=fake_confidence)

        response = authenticated_client.put(
            f"{self.endpoint}/{conversation.entity_id()}",
            json=raw_create_completion_request,
        )

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()

        assert response_data["response"] == fake_llm_response
        assert response_data["confidence"] == fake_confidence
        assert response_data["model"] == raw_create_completion_request["model"]
        assert response_data["provider"] == raw_create_completion_request["provider"]
        assert response_data["question"] == raw_create_completion_request["question"]

    def test_clear_conversation__no_content(
        self,
        conversation_with_completion: Conversation,
        fake_conversation_repository: FakeConversationRepository,
        fake_providers_aggregate: FakeProvidersAggregate,
        fake_event_publisher,
        authenticated_client: TestClient,
    ) -> None:
        fake_conversation_repository.save(conversation_with_completion)

        response = authenticated_client.delete(f"{self.endpoint}/{conversation_with_completion.entity_id()}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_clear_conversation__does_not_exist__not_found(
        self,
        authenticated_client: TestClient,
        fake_conversation_repository: FakeConversationRepository,
        fake_providers_aggregate: FakeProvidersAggregate,
    ) -> None:
        response = authenticated_client.delete(f"{self.endpoint}/unknown_entity_id")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_completions__no_content(
        self,
        conversation_with_completion: Conversation,
        test_completion: Completion,
        fake_conversation_repository: FakeConversationRepository,
        fake_providers_aggregate: FakeProvidersAggregate,
        authenticated_client: TestClient,
    ) -> None:
        fake_conversation_repository.save(conversation_with_completion)

        response = authenticated_client.delete(
            url=f"{self.endpoint}/{conversation_with_completion.entity_id()}/completions",
            params={"completionCodes": [test_completion.code, uuid.uuid4().hex]},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_remove_completions__conversation_does_not_exist__not_found(
        self,
        fake_conversation_repository: FakeConversationRepository,
        fake_providers_aggregate: FakeProvidersAggregate,
        authenticated_client: TestClient,
    ) -> None:
        response = authenticated_client.delete(
            url=f"{self.endpoint}/{uuid.uuid4().hex}/completions",
            params={"completionCodes": uuid.uuid4().hex},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_getting_conversation__conversation_not_exists__created(
        self,
        fake_conversation_repository,
        fake_providers_aggregate,
        authenticated_client: TestClient,
    ) -> None:
        random_id = "random-entity-id"
        response = authenticated_client.get(f"{self.endpoint}/{random_id}")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["conversation"]["entityId"] == random_id
        assert data["conversation"]["completions"] == []

        assert fake_conversation_repository.get(
            entity_id=random_id,
            user_id=test_user_data["subject"],
            tenant_id=test_user_data["organisation"],
        )

    def test_getting_conversation__exists__correct_response_was_built(
        self,
        fake_conversation_repository: FakeConversationRepository,
        fake_providers_aggregate: FakeProvidersAggregate,
        conversation_with_completion: Conversation,
        authenticated_client: TestClient,
    ) -> None:
        fake_conversation_repository.save(conversation_with_completion)

        response = authenticated_client.get(f"{self.endpoint}/{conversation_with_completion.entity_id()}")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["conversation"]["entityId"] == conversation_with_completion.entity_id()

        assert len(data["conversation"]["completions"]) == 1

        first_completion = next(iter(conversation_with_completion.completions.values()))
        first_raw_completion = data["conversation"]["completions"][_FIRST_ELEMENT]

        assert first_raw_completion["model"] == first_completion.llm_reference.model
        assert first_raw_completion["provider"] == first_completion.llm_reference.provider
        assert first_raw_completion["question"] == first_completion.question
        assert first_raw_completion["response"] == first_completion.response

        assert len(data["providers"]) == 1

        provider = fake_providers_aggregate.providers[_FIRST_ELEMENT]
        raw_provider = data["providers"][_FIRST_ELEMENT]
        assert raw_provider["code"] == provider.code
        assert raw_provider["name"] == provider.name

        models_of_provider = fake_providers_aggregate.models_of(provider=provider.code, include_legacy=False)

        assert len(raw_provider["models"]) == len(models_of_provider)

        for i, model in enumerate(models_of_provider):
            assert raw_provider["models"][i]["code"] == model.code
            assert raw_provider["models"][i]["name"] == model.name
            assert raw_provider["models"][i]["contextType"] == model.context_type
