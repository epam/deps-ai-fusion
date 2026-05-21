import json
import random
from typing import Any, Callable
from uuid import uuid4

import pytest
from deps_gen_ai.providers import ProviderCode
from fastapi.testclient import TestClient

from deps_ai_fusion.domain.model import Cardinality, ContextAttachments, DataType
from deps_ai_fusion.entrypoint.api_creators import create_agent_fastapi
from tests.factories import test_user_data


@pytest.fixture
def raw_create_completion_request() -> dict[str, str]:
    return {
        "provider": "provider",
        "model": "model",
        "question": "question",
    }


@pytest.fixture
def raw_retrieve_insights_request(raw_insights_retrival_request_data: dict[str, Any]) -> dict[str, Any]:
    elements = raw_insights_retrival_request_data["elements"]

    raw_elements = {
        code: {"workflow": {"prompts": [{"content": prompt.content} for prompt in query.chain.prompts]}}
        for code, query in elements.items()
    }

    return {
        "documentId": raw_insights_retrival_request_data["entity_id"],
        "filePath": raw_insights_retrival_request_data["filepath"],
        "model": raw_insights_retrival_request_data["llm_reference"],
        "requestedInsights": raw_elements,
        "params": {
            "temperature": raw_insights_retrival_request_data["temperature"],
            "top_p": raw_insights_retrival_request_data["top_p"],
            "groupingFactor": raw_insights_retrival_request_data["retrival_group_size"],
        },
        "customInstructions": raw_insights_retrival_request_data["custom_instructions"],
        "files": raw_insights_retrival_request_data["files"],
    }


@pytest.fixture
def raw_query_with_single_node_request_factory() -> Callable[[str | None], dict[str, Any]]:
    def build(code: str | None = None, node_id: str | None = None, prompt: str | None = None) -> dict[str, Any]:
        node_id = node_id or uuid4().hex
        return {
            "code": code or uuid4().hex,
            "workflow": {
                "startNodeId": node_id,
                "endNodeId": node_id,
                "nodes": [{"id": node_id, "name": f"NAME_{uuid4().hex}", "prompt": prompt or f"PROMPT_{uuid4().hex}"}],
                "edges": [],
            },
            "shape": {"dataType": DataType.STRING, "cardinality": Cardinality.SCALAR, "includeAliases": False},
        }

    return build


@pytest.fixture
def authenticated_client(client):
    client.headers.update(
        {
            "deps-token": json.dumps(test_user_data),
        }
    )

    return client


@pytest.fixture
def request_param() -> dict[str, str]:
    payload = {
        "conversationId": "c1",
        "turnId": "t1",
        "userQuestion": "q",
        "contextBundle": {"conversationTrim": [{"question": "q1", "answer": "a1"}]},
        "arguments": {},
    }

    return {"request": json.dumps(payload)}


@pytest.fixture
def agent_authenticated_client(agent_app):
    with TestClient(agent_app) as client:
        client.headers.update({"deps-token": json.dumps(test_user_data)})
        yield client


@pytest.fixture
def raw_create_llm_extractor_request_data() -> dict[str, Any]:
    return {
        "documentTypeName": "doc_type_name",
        "extractorName": "extractor_name",
        "provider": random.choice(list(ProviderCode)),
        "model": "model_name",
        "extractionParams": {
            "customInstruction": "Custom instruction",
            "groupingFactor": 5,
            "temperature": 0,
            "topP": 1,
            "pageSpan": {"start": 1, "end": 2},
            "contextAttachments": random.choice(list(ContextAttachments)),
        },
    }
