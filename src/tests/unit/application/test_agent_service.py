import pytest
from langgraph.errors import GraphRecursionError

from deps_ai_fusion.application import AgentService
from deps_ai_fusion.domain.exceptions import RequiredArgumentMissing
from deps_ai_fusion.infrastructure.agent import AgentChunk, GenAIQueriesAgent
from tests.fakes import FakeAgent, InMemoryInsightsStore


def test_agent_service_stream_agent_response_yields_chunks_from_impl(
    fake_agent: FakeAgent, agent_chunks: list[AgentChunk], agent_service_factory
) -> None:
    fake_agent.set_chunks(agent_chunks)
    svc = agent_service_factory(fake_agent)

    out = list(
        svc.stream_agent_response(
            conversation_id="c1",
            turn_id="t1",
            user_question="q",
            context_bundle={"conversation_trim": []},
            arguments={},
        )
    )

    assert out == [chunk.to_raw() for chunk in agent_chunks]


def test_agent_service_stream_agent_response_catches_required_argument_missing(
    fake_agent: FakeAgent, agent_service_factory
) -> None:
    fake_agent.set_exception(RequiredArgumentMissing("no doc id"))
    svc = agent_service_factory(fake_agent)

    out = list(
        svc.stream_agent_response(
            conversation_id="c1",
            turn_id="t1",
            user_question="q",
            context_bundle={"conversation_trim": []},
            arguments={},
        )
    )

    assert len(out) == 1
    assert out[0]["type_"] == "Final"
    assert "missing required argument" in out[0]["text"]


def test_agent_service_stream_agent_response_catches_graph_recursion_error(
    fake_agent: FakeAgent, agent_service_factory
) -> None:
    fake_agent.set_exception(GraphRecursionError("boom"))
    svc = agent_service_factory(fake_agent)

    out = list(
        svc.stream_agent_response(
            conversation_id="c1",
            turn_id="t1",
            user_question="q",
            context_bundle={"conversation_trim": []},
            arguments={},
        )
    )

    assert len(out) == 1
    assert out[0]["type_"] == "Final"
    assert "Graph recursion error" in out[0]["text"]


def test_agent_service_stream_agent_response_catches_unexpected_exception(
    fake_agent: FakeAgent, agent_service_factory
) -> None:
    fake_agent.set_exception(RuntimeError("oops"))
    svc = agent_service_factory(fake_agent)

    out = list(
        svc.stream_agent_response(
            conversation_id="c1",
            turn_id="t1",
            user_question="q",
            context_bundle={"conversation_trim": []},
            arguments={},
        )
    )

    assert len(out) == 1
    assert out[0]["type_"] == "Final"
    assert "Unexpected error" in out[0]["text"]


def test_agent_service_register_agent__ok(
    genai_agent: GenAIQueriesAgent, fake_insights_store: InMemoryInsightsStore
) -> None:
    svc = AgentService(agent_implementation=genai_agent, insights_repository=fake_insights_store)
    agent_url = "http://test-agent.com"
    agent_timeout = 30

    svc.register_agent(agent_url=agent_url, agent_timeout=agent_timeout)
    genai_agent._agent_registrator._meta_agent_proxy.register_agent_manifest.assert_called_once_with(
        code="genai-queries-agent",
        name="GenAI Queries Agent",
        description=genai_agent.description,
        agent_url=agent_url,
        timeout=agent_timeout,
    )
    genai_agent._agent_registrator._agentic_ai_proxy.register_tool_set.assert_called_once_with(
        code="genai-queries-agent",
        name="GenAI Queries Agent",
        tools=[{"code": "test-tool", "name": "Test Tool", "parameters": []}],
    )


def test_agent_service_register_agent__register_raises_exception__error(
    genai_agent: GenAIQueriesAgent,
    fake_insights_store: InMemoryInsightsStore,
) -> None:
    genai_agent._agent_registrator._meta_agent_proxy.register_agent_manifest.side_effect = RuntimeError(
        "registration failed"
    )
    svc = AgentService(agent_implementation=genai_agent, insights_repository=fake_insights_store)

    with pytest.raises(RuntimeError) as exc:
        svc.register_agent(agent_url="http://test-agent.com", agent_timeout=30)

    assert "registration failed" in str(exc.value)
