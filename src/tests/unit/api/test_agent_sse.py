from langgraph.errors import GraphRecursionError

from deps_ai_fusion.constants import V1_API_PREFIX
from deps_ai_fusion.domain.exceptions import RequiredArgumentMissing
from deps_ai_fusion.infrastructure.agent import AgentChunk
from tests.fakes import FakeAgent


def _assert_sse_contains_in_order(body: str, first: str, second: str) -> None:
    idx1 = body.find(first)
    idx2 = body.find(second)
    assert idx1 != -1 and idx2 != -1 and idx1 < idx2


def test_agent_sse_stream_success(
    agent_authenticated_client,
    fake_agent: FakeAgent,
    agent_chunks: list[AgentChunk],
    request_param: dict[str, str],
) -> None:
    fake_agent.set_chunks(agent_chunks)

    response = agent_authenticated_client.get(f"{V1_API_PREFIX}/agent/stream", params=request_param)

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/event-stream")

    body = response.text
    _assert_sse_contains_in_order(
        body,
        'data: {"type": "Reasoning", "text": "a"}',
        'data: {"type": "Final", "text": "b"}',
    )


def test_agent_sse_stream_required_argument_missing(
    agent_authenticated_client,
    fake_agent: FakeAgent,
    request_param: dict[str, str],
) -> None:
    fake_agent.set_exception(RequiredArgumentMissing("no doc id"))

    response = agent_authenticated_client.get(f"{V1_API_PREFIX}/agent/stream", params=request_param)

    assert response.status_code == 200
    body = response.text
    assert 'data: {"type": "Final"' in body
    assert "missing required argument" in body


def test_agent_sse_stream_graph_recursion_error(
    agent_authenticated_client,
    fake_agent: FakeAgent,
    request_param: dict[str, str],
) -> None:
    fake_agent.set_exception(GraphRecursionError("boom"))

    response = agent_authenticated_client.get(f"{V1_API_PREFIX}/agent/stream", params=request_param)

    assert response.status_code == 200
    body = response.text
    assert 'data: {"type": "Final"' in body
    assert "Graph recursion error" in body


def test_agent_sse_stream_unexpected_error(
    agent_authenticated_client,
    fake_agent: FakeAgent,
    request_param: dict[str, str],
) -> None:
    fake_agent.set_exception(RuntimeError("oops"))

    response = agent_authenticated_client.get(f"{V1_API_PREFIX}/agent/stream", params=request_param)

    assert response.status_code == 200

    body = response.text
    assert 'data: {"type": "Final"' in body
    assert "Unexpected error" in body
