from deps_ai_fusion.domain.model import Cardinality, DataType
from deps_ai_fusion.infrastructure.agent import AgentState, PerformLLMExtractionTool
from deps_ai_fusion.infrastructure.agent.tools.schemas import DataShape
from tests.factories import AgentStateFactory
from tests.fakes import FakeProvidersAggregate


def test_perform_llm_extraction_calls_providers_and_formats_response(
    perform_llm_extraction_tool: PerformLLMExtractionTool,
    fake_providers_aggregate: FakeProvidersAggregate,
    agent_state_factory: AgentStateFactory,
) -> None:
    fake_providers_aggregate.set_response("hello")

    state: AgentState = agent_state_factory()

    out = perform_llm_extraction_tool._run(
        reasoning="r",
        prompts_chain=["p1"],
        response_model=DataShape(
            data_type=DataType.STRING,
            cardinality=Cardinality.SCALAR,
            include_aliases=False,
        ),
        tool_call_id="tc1",
        state=state,
    )

    assert out.startswith("LLM extraction results: ")
    assert "hello" in out
