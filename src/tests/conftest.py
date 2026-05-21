import random
import uuid
from typing import Any

import pytest
from deps_gen_ai.common import Query as GenAIQuery
from fastapi import FastAPI
from pytest_factoryboy import register
from starlette.testclient import TestClient

from deps_ai_fusion.api import sse
from deps_ai_fusion.application import (
    AnalysisService,
    ConversationService,
    LLMExtractionService,
)
from deps_ai_fusion.containers import Containers
from deps_ai_fusion.domain.model import (
    Cardinality,
    Completion,
    ContextAttachments,
    Conversation,
    DataShape,
    DataType,
    LLMExecutionNode,
    LLMExtractor,
    LLMWorkflow,
    Query,
    RawDataShape,
    RawLLMExecutionNode,
    RawLLMWorkflow,
    RawSequentialEdge,
    SequentialEdge,
)
from deps_ai_fusion.entrypoint import create_agent_fastapi, create_fastapi
from deps_ai_fusion.infrastructure.proxies import (
    ExtractionProxy,
    OriginalImage,
    UnifierProxy,
)
from tests.factories import *
from tests.fakes import FakeFileStorage, FakeProvidersAggregate


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture(scope="session")
def agent_app(app) -> FastAPI:
    app.include_router(sse.router)
    yield app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def containers(app):
    app.containers.reset_singletons()
    return app.containers


@pytest.fixture
def repositories(containers: Containers):
    return containers.repositories


@pytest.fixture
def test_command_channel():
    return None


@pytest.fixture
def conversation_service(containers: Containers) -> ConversationService:
    return containers.conversation_service()


@pytest.fixture
def analysis_service(containers: Containers) -> AnalysisService:
    return containers.analysis_service()


@pytest.fixture
def llm_extraction_service(containers: Containers) -> LLMExtractionService:
    return containers.llm_extraction_service()


@pytest.fixture
def fake_providers_aggregate(containers: Containers) -> FakeProvidersAggregate:  # type: ignore
    with containers.providers_aggregate.override(FakeProvidersAggregate()):
        yield containers.providers_aggregate()


@pytest.fixture
def llms_controller_with_fakes(fake_providers_aggregate: FakeProvidersAggregate, containers: Containers) -> FakeProvidersAggregate:  # type: ignore
    with containers.reset_singletons():
        yield containers.services.llms_controller()


@pytest.fixture
def fake_file_storage(containers: Containers) -> FakeFileStorage:  # type: ignore
    with containers.proxies.file_storage.override(FakeFileStorage()):
        yield containers.proxies.file_storage()


@pytest.fixture
def mock_extraction(mocker, containers: Containers) -> ExtractionProxy:  # type: ignore
    with containers.proxies.extraction.override(mocker.Mock(containers.proxies.extraction.cls)):
        yield containers.proxies.extraction()


@pytest.fixture
def mock_unifier(mocker, containers: Containers) -> UnifierProxy:  # type: ignore
    with containers.proxies.unifier.override(mocker.Mock(containers.proxies.unifier.cls)):
        yield containers.proxies.unifier()


@pytest.fixture
def unifier_proxy_return_value() -> list[OriginalImage]:
    return [OriginalImage(id=uuid.uuid4().hex, page=1, path="file_path")]  # type: ignore


@pytest.fixture
def raw_completion_data() -> dict[str, Any]:
    return {
        "provider": "provider",
        "model": "model",
        "question": "question",
        "response": "response",
        "confidence": 0.25,
    }


@pytest.fixture
def raw_insights_retrival_request_data() -> dict[str, Any]:
    return {
        "entity_id": "12345",
        "filepath": "/some-file/path.pdf",
        "llm_reference": "model",
        "elements": {
            "code1": GenAIQuery.from_raw(["prompt 1"]),
            "code2": GenAIQuery.from_raw(["prompt 2"]),
        },
        "custom_instructions": "custom instructions",
        "temperature": 0.5,
        "top_p": 0.5,
        "retrival_group_size": 10,
        "files": ["file1.png", "file2.png"],
    }


@pytest.fixture
def test_completion(conversation: Conversation, raw_completion_data: dict[str, Any]) -> Completion:
    return conversation.add_completion(
        provider=raw_completion_data["provider"],
        model=raw_completion_data["model"],
        question=raw_completion_data["question"],
        response=raw_completion_data["response"],
        confidence=raw_completion_data["confidence"],
    )


@pytest.fixture
def conversation_with_completion(conversation: Conversation, test_completion: Completion) -> Conversation:
    return conversation


@pytest.fixture
def tenant_id() -> str:
    return test_user_data["organisation"]


@pytest.fixture
def llm_extractor_id() -> str:
    return uuid.uuid4().hex


@pytest.fixture
def document_type_id() -> str:
    return uuid.uuid4().hex


@pytest.fixture
def llm_extractor(llm_extractor_id: str, document_type_id: str, tenant_id: str) -> LLMExtractor:
    return LLMExtractorFactory.create(
        id_=llm_extractor_id,
        document_type_id=document_type_id,
        tenant_id=tenant_id,
    )


@pytest.fixture
def llm_extractor__no_page_span(llm_extractor_id: str, document_type_id: str, tenant_id: str) -> LLMExtractor:
    return LLMExtractorFactory.create(
        id_=llm_extractor_id,
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        extraction_params=ExtractionParamsFactory(page_span=None),
    )


@pytest.fixture
def test_code() -> str:
    return uuid.uuid4().hex


@pytest.fixture
def test_llm_workflow() -> LLMWorkflow:
    node_ids = [uuid.uuid4().hex for _ in range(random.randint(2, 10))]
    nodes = []
    edges = []

    for ind, id_ in enumerate(node_ids):
        nodes.append(LLMExecutionNode(id_=id_, name=f"Node #{ind + 1}", prompt=uuid.uuid4().hex))

    for ind in range(len(node_ids) - 1):
        edges.append(SequentialEdge(source_id=node_ids[ind], target_id=node_ids[ind + 1]))

    return LLMWorkflow(
        entrypoint_node_id=nodes[0].id,
        output_node_id=nodes[-1].id,
        nodes=nodes,
        edges=edges,
    )


@pytest.fixture
def test_raw_llm_workflow() -> RawLLMWorkflow:
    node_ids = [uuid.uuid4().hex for _ in range(random.randint(2, 10))]
    nodes = []
    edges = []

    for ind, id_ in enumerate(node_ids):
        nodes.append(RawLLMExecutionNode(id=id_, name=f"Node #{ind + 1}", prompt=uuid.uuid4().hex))

    for ind in range(len(node_ids) - 1):
        edges.append(RawSequentialEdge(source_id=node_ids[ind], target_id=node_ids[ind + 1]))

    return RawLLMWorkflow(
        start_node_id=nodes[0]["id"],
        end_node_id=nodes[-1]["id"],
        nodes=nodes,
        edges=edges,
    )


@pytest.fixture
def test_raw_data_shape() -> RawDataShape:
    cardinality = random.choice([Cardinality.SCALAR, Cardinality.LIST])
    return RawDataShape(
        data_type=random.choice(list(DataType)),
        cardinality=cardinality,
        include_aliases=False if cardinality == Cardinality.SCALAR else random.choice([True, False]),
    )


@pytest.fixture
def test_query(test_code: str, test_llm_workflow: LLMWorkflow) -> Query:
    return Query(
        code=test_code,
        workflow=test_llm_workflow,
        shape=DataShape(
            data_type=random.choice(list(DataType)),
            cardinality=random.choice(list(Cardinality)),
        ),
    )


@pytest.fixture
def llm_extractor_with_query(
    llm_extractor: LLMExtractor,
    test_code: str,
    test_raw_llm_workflow: RawLLMWorkflow,
    test_raw_data_shape: RawDataShape,
) -> LLMExtractor:
    llm_extractor.add_query(
        code=test_code,
        workflow=test_raw_llm_workflow,
        data_shape=test_raw_data_shape,
    )

    return llm_extractor


@pytest.fixture
def llm_extractor_no_context_attachments(llm_extractor_id: str, document_type_id: str, tenant_id: str) -> LLMExtractor:
    return LLMExtractorFactory.create(
        id_=llm_extractor_id,
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        extraction_params=ExtractionParamsFactory(context_attachments=None),
    )


register(ConversationFactory)
register(LLMExtractorFactory)
register(ExtractionParamsFactory)
register(PageSpanFactory)
register(LLMReferenceFactory)
register(QueryFactory)
register(AgentStateFactory)
