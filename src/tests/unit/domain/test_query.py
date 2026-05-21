from uuid import uuid4

import pytest

from deps_ai_fusion.domain.exceptions import IllegalArgument
from deps_ai_fusion.domain.model import (
    Cardinality,
    DataShape,
    DataType,
    Query,
    RawLLMExecutionNode,
    RawLLMWorkflow,
    RawSequentialEdge,
)


def test_update_query__updated(test_llm_workflow):
    expected_prompt_change = uuid4().hex

    query = Query(
        code=uuid4().hex,
        workflow=test_llm_workflow,
        shape=DataShape(data_type=DataType.STRING, cardinality=Cardinality.SCALAR, include_aliases=False),
    )
    updated_llm_workflow = RawLLMWorkflow(
        start_node_id=test_llm_workflow.entrypoint_node_id,
        end_node_id=test_llm_workflow.output_node_id,
        nodes=[
            RawLLMExecutionNode(id=node.id, name=node.name, prompt=node.prompt + "_" + expected_prompt_change)
            for node in test_llm_workflow.nodes
        ],
        edges=[
            RawSequentialEdge(source_id=edge.source_id, target_id=edge.target_id) for edge in test_llm_workflow.edges
        ],
    )

    query.update(updated_llm_workflow)

    for node in query.workflow.nodes:
        assert expected_prompt_change in node.prompt


def test_change_data_shape__error(test_llm_workflow):
    query = Query(
        code=uuid4().hex,
        workflow=test_llm_workflow,
        shape=DataShape(data_type=DataType.STRING, cardinality=Cardinality.SCALAR, include_aliases=False),
    )

    with pytest.raises(IllegalArgument):
        new_shape = DataShape(data_type=DataType.STRING, cardinality=Cardinality.LIST, include_aliases=False)
        query.shape = new_shape

    with pytest.raises(IllegalArgument):
        query.shape.cardinality = Cardinality.LIST

    with pytest.raises(IllegalArgument):
        query.shape.data_type = DataType.BOOLEAN

    with pytest.raises(IllegalArgument):
        query.shape.include_aliases = False
