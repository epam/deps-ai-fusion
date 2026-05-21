import pytest

from deps_ai_fusion.domain.model import Cardinality, DataShape, DataType
from deps_ai_fusion.infrastructure.services.llm_extraction import (
    BooleanResponse,
    BooleansListResponse,
    BooleansListWithAliasesResponse,
    GenAIQueryFactory,
    KeyValuePairResponse,
    KeyValuePairsListResponse,
    KeyValuePairsListWithAliasesResponse,
    StringResponse,
    StringsListResponse,
    StringsListWithAliasesResponse,
)
from tests.factories.query import QueryFactory


@pytest.mark.parametrize(
    "data_type, cardinality, include_aliases, expected_model",
    [
        (DataType.STRING, Cardinality.SCALAR, False, StringResponse),
        (DataType.BOOLEAN, Cardinality.SCALAR, False, BooleanResponse),
        (DataType.KEY_VALUE_PAIR, Cardinality.SCALAR, False, KeyValuePairResponse),
        (DataType.STRING, Cardinality.LIST, False, StringsListResponse),
        (DataType.BOOLEAN, Cardinality.LIST, False, BooleansListResponse),
        (DataType.KEY_VALUE_PAIR, Cardinality.LIST, False, KeyValuePairsListResponse),
        (DataType.STRING, Cardinality.LIST, True, StringsListWithAliasesResponse),
        (DataType.BOOLEAN, Cardinality.LIST, True, BooleansListWithAliasesResponse),
        (DataType.KEY_VALUE_PAIR, Cardinality.LIST, True, KeyValuePairsListWithAliasesResponse),
    ],
)
def test_genai_query_factory__maps_response_model_and_prompts(
    data_type: DataType,
    cardinality: Cardinality,
    include_aliases: bool,
    expected_model: type,
) -> None:
    # Override shape to concrete parametrized combination
    query = QueryFactory(shape=DataShape(data_type=data_type, cardinality=cardinality, include_aliases=include_aliases))

    factory = GenAIQueryFactory()
    genai_query = factory.genai_query_from_domain(query)

    assert genai_query.response_model is expected_model

    prompts = [prompt.content for prompt in genai_query.chain.prompts]
    assert prompts == [node.prompt for node in query.workflow.nodes]
