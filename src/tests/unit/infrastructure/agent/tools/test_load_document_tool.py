from deps_gen_ai.common import ContextReference

from deps_ai_fusion.infrastructure.agent import AgentState, DocumentLoadingTool
from tests.factories import AgentStateFactory


def test_document_loading_tool_returns_context(
    document_loading_tool: DocumentLoadingTool,
    mock_layout_context_creator,
    agent_state_factory: AgentStateFactory,
) -> None:
    fake_context_text = "the full document context"
    state: AgentState = agent_state_factory()

    mock_layout_context_creator.set_context_response(state.document_id, fake_context_text)

    out = document_loading_tool._run(reasoning="r", state=state)

    assert out == fake_context_text
