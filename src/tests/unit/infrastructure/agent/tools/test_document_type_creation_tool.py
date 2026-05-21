import pytest

from deps_ai_fusion.infrastructure.agent import AgentState, DocumentTypeCreationTool
from tests.factories import AgentStateFactory


def test_document_type_creation_creates_when_no_document_type(
    document_type_creation_tool: DocumentTypeCreationTool,
    mocker,
    agent_state_factory: AgentStateFactory,
) -> None:
    state: AgentState = agent_state_factory(document_type_id=None)
    mocker.patch.object(
        document_type_creation_tool.extractors_app, "create_extractor", return_value=("dt-id", "ext-id")
    )

    cmd = document_type_creation_tool._run(
        document_type_name="Invoices",
        reasoning="r",
        tool_call_id="tc1",
        state=state,
    )

    assert cmd.update["document_type_id"] == "dt-id"
    assert cmd.update["extractor_id"] == "ext-id"
    assert state.document_type_id is None


def test_document_type_creation_raises_if_document_type_present(
    document_type_creation_tool: DocumentTypeCreationTool,
    agent_state_factory: AgentStateFactory,
) -> None:
    state: AgentState = agent_state_factory(document_type_id="dt-1")

    with pytest.raises(RuntimeError):
        document_type_creation_tool._run(
            document_type_name="Name",
            reasoning="r",
            tool_call_id="tc1",
            state=state,
        )
