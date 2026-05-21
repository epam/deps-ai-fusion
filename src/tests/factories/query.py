import random
import uuid
from typing import cast

import factory

from deps_ai_fusion.domain.model.llm_extractor.query import (
    Cardinality,
    Code,
    DataShape,
    DataType,
    Edge,
    LLMExecutionNode,
    LLMWorkflow,
    Node,
    Query,
    SequentialEdge,
)

__all__ = ["QueryFactory"]


def _make_linear_workflow(num_nodes: int = 3) -> LLMWorkflow:
    node_ids = [uuid.uuid4().hex for _ in range(num_nodes)]
    nodes = [LLMExecutionNode(id_=node_ids[i], name=f"Node #{i+1}", prompt=f"prompt-{i+1}") for i in range(num_nodes)]
    edges = [SequentialEdge(source_id=node_ids[i], target_id=node_ids[i + 1]) for i in range(num_nodes - 1)]
    return LLMWorkflow(
        entrypoint_node_id=node_ids[0],
        output_node_id=node_ids[-1],
        nodes=cast(list[Node], nodes),
        edges=cast(list[Edge], edges),
    )


class QueryFactory(factory.Factory):
    class Meta:
        model = Query

    code: Code = factory.LazyFunction(lambda: uuid.uuid4().hex)
    workflow: LLMWorkflow = factory.LazyFunction(_make_linear_workflow)
    shape: DataShape = factory.LazyFunction(
        lambda: DataShape(
            data_type=random.choice(list(DataType)),
            cardinality=random.choice(list(Cardinality)),
            include_aliases=False,
        )
    )
