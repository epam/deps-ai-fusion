import uuid
from uuid import uuid4

import pytest

from deps_ai_fusion.domain.exceptions import IllegalArgument, InvariantViolationError
from deps_ai_fusion.domain.model import LLMExecutionNode, LLMWorkflow, SequentialEdge


def test_llm_workflow__no_nodes__error():
    with pytest.raises(IllegalArgument):
        LLMWorkflow(
            entrypoint_node_id=uuid4().hex,
            output_node_id=uuid4().hex,
            nodes=[],
            edges=[],
        )


def test_llm_workflow__no_edges__no_error():
    node_id = uuid4().hex
    workflow = LLMWorkflow(
        entrypoint_node_id=node_id,
        output_node_id=node_id,
        nodes=[LLMExecutionNode(id_=node_id, name="test_name", prompt="test_prompt")],
        edges=[],
    )
    assert workflow.edges == []


def test_llm_workflow__entrypoint_node_id_not_belogns_to_nodes__error():
    node_id = uuid4().hex
    wrong_id = uuid4().hex

    with pytest.raises(InvariantViolationError) as err:
        LLMWorkflow(
            entrypoint_node_id=wrong_id,
            output_node_id=node_id,
            nodes=[LLMExecutionNode(id_=node_id, name="test_name", prompt="test_prompt")],
            edges=[],
        )

    assert err.value.details == f"LLMWorkflow entrypoint node ID '{wrong_id}' not found in nodes."


def test_llm_workflow__output_node_id_not_belogns_to_nodes__error():
    node_id = uuid4().hex
    wrong_id = uuid4().hex

    with pytest.raises(InvariantViolationError) as err:
        LLMWorkflow(
            entrypoint_node_id=node_id,
            output_node_id=wrong_id,
            nodes=[LLMExecutionNode(id_=node_id, name="test_name", prompt="test_prompt")],
            edges=[],
        )

    assert err.value.details == f"LLMWorkflow output node ID '{wrong_id}' not found in nodes."


@pytest.mark.parametrize("wrong_node_id", [uuid.uuid1().hex, "wrong_string"])
def test_llm_workflow__node_id_not_valid_uuid4__error(wrong_node_id):
    with pytest.raises(InvariantViolationError) as err:
        LLMWorkflow(
            entrypoint_node_id=wrong_node_id,
            output_node_id=wrong_node_id,
            nodes=[LLMExecutionNode(id_=wrong_node_id, name="test_name", prompt="test_prompt")],
            edges=[],
        )

    assert err.value.details == "LLMWorkflow invalid UUID4 string for node ID."


def test_llm_workflow__wrong_first_edge__error():
    with pytest.raises(InvariantViolationError) as err:
        node_ids = [uuid4().hex for _ in range(5)]
        nodes = []
        edges = []

        for ind, id_ in enumerate(node_ids[:-1], 1):
            nodes.append(LLMExecutionNode(id_=id_, name=f"Node #{ind}", prompt=uuid4().hex))
            edges.append(SequentialEdge(source_id=id_, target_id=node_ids[ind]))
        nodes.append(LLMExecutionNode(id_=node_ids[-1], name=f"Node #{len(node_ids)}", prompt=uuid4().hex))

        edges[0]._source_id = "wrong_id"
        return LLMWorkflow(
            entrypoint_node_id=nodes[0].id,
            output_node_id=nodes[-1].id,
            nodes=nodes,
            edges=edges,
        )

    assert err.value.details == "LLMWorkflow graph structure is invalid: missing edge."


def test_llm_workflow__has_cycle_edge__error():
    node_ids = [uuid4().hex for _ in range(5)]
    nodes = []
    edges = []

    for ind, id_ in enumerate(node_ids[:-1], 1):
        nodes.append(LLMExecutionNode(id_=id_, name=f"Node #{ind}", prompt=uuid4().hex))
        edges.append(SequentialEdge(source_id=id_, target_id=node_ids[ind]))

    nodes.append(LLMExecutionNode(id_=node_ids[-1], name=f"Node #{len(node_ids)}", prompt=uuid4().hex))

    edges[-1]._target_id = node_ids[0]

    with pytest.raises(InvariantViolationError) as err:
        return LLMWorkflow(
            entrypoint_node_id=nodes[0].id,
            output_node_id=nodes[-1].id,
            nodes=nodes,
            edges=edges,
        )

    assert err.value.details == "LLMWorkflow graph must be acyclic."


def test_llm_workflow__has_less_edges__error():
    node_ids = [uuid4().hex for _ in range(5)]
    nodes = []
    edges = []

    for ind, id_ in enumerate(node_ids[:-1], 1):
        nodes.append(LLMExecutionNode(id_=id_, name=f"Node #{ind}", prompt=uuid4().hex))
        edges.append(SequentialEdge(source_id=id_, target_id=node_ids[ind]))

    nodes.append(LLMExecutionNode(id_=node_ids[-1], name=f"Node #{len(node_ids)}", prompt=uuid4().hex))

    edges.pop()

    with pytest.raises(InvariantViolationError) as err:
        return LLMWorkflow(
            entrypoint_node_id=nodes[0].id,
            output_node_id=nodes[-1].id,
            nodes=nodes,
            edges=edges,
        )

    assert err.value.details == "LLMWorkflow graph structure is invalid: edges must connect all nodes."


def test_llm_workflow__has_duplicated_node_id__error():
    id_ = uuid4().hex
    node_ids = [id_ for _ in range(2)]
    nodes = []
    edges = []

    for ind, id_ in enumerate(node_ids[:-1], 1):
        nodes.append(LLMExecutionNode(id_=id_, name=f"Node #{ind}", prompt=uuid4().hex))
        edges.append(SequentialEdge(source_id=id_, target_id=node_ids[ind]))

    nodes.append(LLMExecutionNode(id_=node_ids[-1], name=f"Node #{len(node_ids)}", prompt=uuid4().hex))

    with pytest.raises(InvariantViolationError) as err:
        return LLMWorkflow(
            entrypoint_node_id=nodes[0].id,
            output_node_id=nodes[-1].id,
            nodes=nodes,
            edges=edges,
        )

    assert err.value.details == "LLMWorkflow has duplicate node IDs found in the graph."
