from uuid import uuid4

import pytest
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_ai_fusion.application import LLMExtractionService
from deps_ai_fusion.infrastructure.access_management import user
from deps_ai_fusion.infrastructure.agent import (
    AgentChunk,
    DocumentLoadingTool,
    DocumentTypeCreationTool,
    GenAIFieldCreationTool,
    PerformLLMExtractionTool,
)
from tests.factories import AgentStateFactory
from tests.fakes import (
    FakeAgent,
    FakeConversationRepository,
    FakeEventPublisher,
    FakeExtractionProxy,
    FakeLLMExtractorRepository,
    FakePlainLayoutContextCreator,
)
from tests.fakes.insights_store import InMemoryInsightsStore


@pytest.fixture
def postgres_datasource_mock(mocker, containers):  # type: ignore
    mock = mocker.Mock(containers.datasources.postgres_datasource())
    containers.datasources.postgres_datasource.override(mock)

    yield mock

    containers.datasources.reset_override()


@pytest.fixture
def fake_conversation_repository(repositories) -> FakeConversationRepository:  # type: ignore
    repositories.reset_singletons()
    with repositories.conversation_repository.override(FakeConversationRepository()):
        yield repositories.conversation_repository()


@pytest.fixture
def fake_llm_extractor_repository(repositories) -> FakeLLMExtractorRepository:  # type: ignore
    repositories.reset_singletons()
    with repositories.llm_extractor_repository.override(FakeLLMExtractorRepository()):
        yield repositories.llm_extractor_repository()


@pytest.fixture
def fake_event_publisher(containers) -> FakeEventPublisher:  # type: ignore
    containers.reset_singletons()
    with containers.domain_event_publisher.override(FakeEventPublisher()):
        yield containers.domain_event_publisher()


@pytest.fixture
def fake_insights_repository(containers) -> InMemoryInsightsStore:  # type: ignore
    containers.reset_singletons()
    with containers.repositories.insights_repository.override(InMemoryInsightsStore()):
        yield containers.repositories.insights_repository()


@pytest.fixture
def mock_extraction_service(mocker, containers) -> LLMExtractionService:  # type: ignore
    containers.reset_singletons()
    with containers.llm_extraction_service.override(mocker.Mock(containers.llm_extraction_service.cls)):
        yield containers.llm_extraction_service()


@pytest.fixture
def mock_layout_context_creator(containers):
    containers.reset_singletons()
    fake = FakePlainLayoutContextCreator()
    with containers.services.layout_context_creator.override(fake):
        yield fake


@pytest.fixture
def mock_extraction_proxy(containers):
    containers.reset_singletons()
    fake = FakeExtractionProxy()
    with containers.proxies.extraction.override(fake):
        yield fake


@pytest.fixture
def document_loading_tool(containers, mock_layout_context_creator) -> DocumentLoadingTool:
    return containers.agent.document_loading_tool()


@pytest.fixture
def genai_field_creation_tool(
    containers,
    mock_extraction_proxy,
    fake_llm_extractor_repository,
) -> GenAIFieldCreationTool:
    return containers.agent.genai_field_creation()


@pytest.fixture
def perform_llm_extraction_tool(
    containers,
    fake_providers_aggregate,
    llm_extraction_service,
) -> PerformLLMExtractionTool:
    return containers.agent.perform_llm_extraction()


@pytest.fixture
def document_type_creation_tool(containers) -> DocumentTypeCreationTool:
    return containers.agent.document_type_creation()


@pytest.fixture
def fake_agent(containers):
    containers.reset_singletons()
    with containers.agent.implementation.override(FakeAgent()):
        yield containers.agent.implementation()


@pytest.fixture
def agent_chunks() -> list[AgentChunk]:
    return [AgentChunk(type_="Reasoning", text="a"), AgentChunk(type_="Final", text="b")]


@pytest.fixture
def agent_state_factory():
    return AgentStateFactory


@pytest.fixture
def perform_llm_extraction_command(mocker) -> CommandMessage:
    command_message = mocker.Mock(CommandMessage)
    command_message.command.extractor_id = uuid4().hex
    command_message.command.document_id = uuid4().hex
    command_message.command.llm_type = None

    return command_message


@pytest.fixture
def extractor_field_deleted_event(mocker) -> DomainEventEnvelope:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.code = uuid4().hex
    dee.event.extractor_id = uuid4().hex
    dee.event.extractor_type = uuid4().hex
    dee.event.document_type_code = uuid4().hex

    return dee


@pytest.fixture
def conversation_deleted_event(mocker) -> DomainEventEnvelope:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.id = uuid4().hex

    return dee


@pytest.fixture
def fake_insights_store():
    from tests.fakes.insights_store import InMemoryInsightsStore

    return InMemoryInsightsStore()


@pytest.fixture
def agent_service_factory(fake_insights_store):
    from deps_ai_fusion.application import AgentService

    def _factory(fake_agent):
        return AgentService(agent_implementation=fake_agent, insights_repository=fake_insights_store)

    return _factory


@pytest.fixture
def fake_agent_service(fake_agent, fake_insights_store):
    from deps_ai_fusion.application import AgentService

    return AgentService(agent_implementation=fake_agent, insights_repository=fake_insights_store)


@pytest.fixture(autouse=True)
def set_user(tenant_id):
    user.set(
        {
            "organisation": tenant_id,
            "subject": "subject",
            "roles": [],
            "groups": [tenant_id],
        }
    )
