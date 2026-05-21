from typing import TypeAlias

from deps_gen_ai.common import Query as GenAIQuery
from pydantic import BaseModel

from deps_ai_fusion.domain.model import (
    Cardinality,
    DataType,
    LLMExecutionNode,
    Query,
    SequentialEdge,
)

from .response_models import (
    BooleanResponse,
    BooleansListResponse,
    BooleansListWithAliasesResponse,
    KeyValuePairResponse,
    KeyValuePairsListResponse,
    KeyValuePairsListWithAliasesResponse,
    StringResponse,
    StringsListResponse,
    StringsListWithAliasesResponse,
)

__all__ = ["GenAIQueryFactory"]

NodeId: TypeAlias = str
IncludeAliases: TypeAlias = bool


class GenAIQueryFactory:
    def __init__(self) -> None:
        self.response_model_for_dtype: dict[tuple[DataType, Cardinality, IncludeAliases], type[BaseModel]] = {
            (DataType.STRING, Cardinality.SCALAR, False): StringResponse,
            (DataType.BOOLEAN, Cardinality.SCALAR, False): BooleanResponse,
            (DataType.KEY_VALUE_PAIR, Cardinality.SCALAR, False): KeyValuePairResponse,
            (DataType.STRING, Cardinality.LIST, False): StringsListResponse,
            (DataType.BOOLEAN, Cardinality.LIST, False): BooleansListResponse,
            (DataType.KEY_VALUE_PAIR, Cardinality.LIST, False): KeyValuePairsListResponse,
            (DataType.STRING, Cardinality.LIST, True): StringsListWithAliasesResponse,
            (DataType.BOOLEAN, Cardinality.LIST, True): BooleansListWithAliasesResponse,
            (DataType.KEY_VALUE_PAIR, Cardinality.LIST, True): KeyValuePairsListWithAliasesResponse,
        }

    def genai_query_from_domain(self, query: Query) -> GenAIQuery:
        # Currently we have only LLMExecutionNode and SequentialEdge, checks needed for typing
        # GenAIQuery doesn't support more complicated workflows either
        node_prompts: dict[NodeId, str] = {
            node.id: node.prompt for node in query.workflow.nodes if isinstance(node, LLMExecutionNode)
        }
        node_relations: dict[NodeId, NodeId] = {
            edge.source_id: edge.target_id for edge in query.workflow.edges if isinstance(edge, SequentialEdge)
        }

        # We have domain invariant that workflow doesn't contain cycles or unconnected nodes,
        # so we can simply traverse the workflow linearly from the entrypoint node, following each edge in sequence
        prompts: list[str] = []
        current_node: str = query.workflow.entrypoint_node_id
        for _ in node_prompts:
            prompts.append(node_prompts[current_node])

            if current_node == query.workflow.output_node_id:
                break

            current_node = node_relations[current_node]

        return GenAIQuery.from_raw(
            prompts=prompts,
            response_model=self.response_model_for_dtype[
                (query.shape.data_type, query.shape.cardinality, query.shape.include_aliases)
            ],
        )
