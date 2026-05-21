import pytest

from deps_ai_fusion.application.types import RawAgentArguments, RawContextBundle
from deps_ai_fusion.domain.exceptions import RequiredArgumentMissing
from deps_ai_fusion.infrastructure.agent.state import AgentState


def _make_args(document_id: str | None = "doc-1", document_type_id: str | None = None) -> RawAgentArguments:
    args: RawAgentArguments = {}

    if document_id is not None:
        args["document_id"] = [{"value": document_id}]
    if document_type_id is not None:
        args["document_type_id"] = [{"value": document_type_id}]

    return args


def _make_context(conversation: list[tuple[str, str]]) -> RawContextBundle:
    return {
        "conversation_trim": [{"question": q, "answer": a} for q, a in conversation],
    }


def test_agent_state_from_arguments_builds_state_with_messages_and_ids() -> None:
    args = _make_args("d-123", "type-9")
    context = _make_context([("q1", "a1"), ("q2", "a2")])

    state = AgentState.from_arguments(conversation_id="c1", args=args, context=context, question="new question")

    assert state.document_id == "d-123"
    assert state.document_type_id == "type-9"

    # conversation_trim transformed to alternating Human/AI messages + final Human question
    assert len(state.messages) == 2 * len(context["conversation_trim"]) + 1
    assert str(state.messages[-1].content) == "new question"


def test_agent_state_from_arguments_handles_optional_document_type_id() -> None:
    args = _make_args("d-123", None)
    context = _make_context([])

    state = AgentState.from_arguments(conversation_id="c1", args=args, context=context, question="q")

    assert state.document_id == "d-123"
    assert state.document_type_id is None
    assert len(state.messages) == 1
    assert str(state.messages[0].content) == "q"


def test_agent_state_from_arguments_raises_when_document_id_missing() -> None:
    args = _make_args(None, None)
    context = _make_context([])

    with pytest.raises(RequiredArgumentMissing):
        AgentState.from_arguments(conversation_id="c1", args=args, context=context, question="q")
