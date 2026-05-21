from dataclasses import dataclass

import pytest
from deps_extracted_data.model import CheckboxValue, ExtractedDataFactory
from deps_extracted_data.model.extracted_data.data_types.factory import FieldDataFactory

from deps_ai_fusion.domain.model import Cardinality, DataShape, DataType
from deps_ai_fusion.infrastructure.services.llm_extraction import (
    BooleanResponse,
    BooleansListResponse,
    BooleansListWithAliasesResponse,
    InsightsRecorder,
    KeyValuePairResponse,
    KeyValuePairsListResponse,
    KeyValuePairsListWithAliasesResponse,
    StringResponse,
    StringsListResponse,
    StringsListWithAliasesResponse,
)
from deps_ai_fusion.infrastructure.services.llm_extraction.genai_query_factory.response_models.aliases import (
    BooleanItemWithAlias,
    KeyValuePairItemWithAlias,
    StringItemWithAlias,
)
from tests.factories import QueryFactory


@dataclass
class _Resp:
    content: str
    parsed: object
    success: bool = True
    confidence: float | None = 0.77


def test_record_string_adds_string_field() -> None:
    query = QueryFactory.create(shape=DataShape(data_type=DataType.STRING, cardinality=Cardinality.SCALAR))
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(content='{"value": "hello"}', parsed=StringResponse(reasoning="r", value="hello"))

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    assert edata.has_field(query.code)
    field = edata.get(query.code)
    assert field is not None
    assert field.data.value == "hello"
    assert field.data.confidence == 0.77


def test_record_boolean_adds_checkbox_field() -> None:
    query = QueryFactory.create(shape=DataShape(data_type=DataType.BOOLEAN, cardinality=Cardinality.SCALAR))
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(content='{"value": true}', parsed=BooleanResponse(reasoning="r", value=True))

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    assert edata.has_field(query.code)
    field = edata.get(query.code)
    assert field is not None
    assert field.data.value.mapped_value is True
    assert field.data.confidence == 0.77


def test_record_key_value_pair_adds_field() -> None:
    query = QueryFactory.create(shape=DataShape(data_type=DataType.KEY_VALUE_PAIR, cardinality=Cardinality.SCALAR))
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(content='{"key": "k", "value": "v"}', parsed=KeyValuePairResponse(reasoning="r", key="k", value="v"))

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    assert edata.has_field(query.code)
    field = edata.get(query.code)
    assert field is not None
    assert field.data.key.value == "k"
    assert field.data.value.value == "v"
    assert field.data.key.confidence == 0.77
    assert field.data.value.confidence == 0.77


def test_record_strings_list_adds_list_field() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.STRING, cardinality=Cardinality.LIST, include_aliases=False)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed=StringsListResponse(
            values=[
                StringResponse(reasoning="r1", value="a"),
                StringResponse(reasoning="r2", value="b"),
            ]
        ),
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    assert edata.has_field(query.code)
    field = edata.get(query.code)
    assert field is not None
    assert [el.value for el in field.data.elements] == ["a", "b"]


def test_record_booleans_list_adds_list_field() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.BOOLEAN, cardinality=Cardinality.LIST, include_aliases=False)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed=BooleansListResponse(
            values=[
                BooleanResponse(reasoning="r1", value=True),
                BooleanResponse(reasoning="r2", value=False),
            ]
        ),
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    assert edata.has_field(query.code)
    field = edata.get(query.code)
    assert field is not None
    assert [el.value.mapped_value for el in field.data.elements] == [True, False]


def test_record_key_value_pairs_list_adds_list_field() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.KEY_VALUE_PAIR, cardinality=Cardinality.LIST, include_aliases=False)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed=KeyValuePairsListResponse(
            items=[
                KeyValuePairResponse(reasoning="r1", key="k1", value="v1"),
                KeyValuePairResponse(reasoning="r2", key="k2", value="v2"),
            ]
        ),
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    assert edata.has_field(query.code)
    field = edata.get(query.code)
    assert field is not None
    assert [{"key": kv.key.value, "value": kv.value.value} for kv in field.data.elements] == [
        {"key": "k1", "value": "v1"},
        {"key": "k2", "value": "v2"},
    ]


def test_record_strings_list_with_aliases_adds_aliases() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.STRING, cardinality=Cardinality.LIST, include_aliases=True)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed=StringsListWithAliasesResponse(
            items=[
                StringItemWithAlias(reasoning="r1", value="a", alias="A"),
                StringItemWithAlias(reasoning="r2", value="b", alias="B"),
            ]
        ),
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    field = edata.get(query.code)
    assert field is not None
    assert [el.value for el in field.data.elements] == ["a", "b"]
    assert sorted(field.data.aliases.values()) == ["A", "B"]


def test_record_strings_list_with_empty_aliases_skips_invalid_aliases() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.STRING, cardinality=Cardinality.LIST, include_aliases=True)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed={
            "items": [
                {"value": "a", "alias": "ValidAlias"},
                {"value": "b", "alias": ""},
                {"value": "c", "alias": "   "},
                {"value": "d", "alias": "AnotherValid"},
            ]
        },
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    field = edata.get(query.code)
    assert field is not None
    assert [el.value for el in field.data.elements] == ["a", "b", "c", "d"]
    assert sorted(field.data.aliases.values()) == ["AnotherValid", "ValidAlias"]


def test_field_data_factory_create_string_list_with_empty_alias_raises_error() -> None:
    factory = FieldDataFactory()
    element1 = factory.create_string(value="test1")
    element2 = factory.create_string(value="test2")

    with pytest.raises(RuntimeError, match="Alias for element.*can't be added"):
        factory.create_generic_list(
            elements=[element1, element2],
            aliases={element1.id: "", element2.id: "ValidAlias"},
        )


def test_record_booleans_list_with_aliases_adds_aliases() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.BOOLEAN, cardinality=Cardinality.LIST, include_aliases=True)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed=BooleansListWithAliasesResponse(
            items=[
                BooleanItemWithAlias(reasoning="r1", value=True, alias="T"),
                BooleanItemWithAlias(reasoning="r2", value=False, alias="F"),
            ]
        ),
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    field = edata.get(query.code)
    assert field is not None
    assert [el.value.mapped_value for el in field.data.elements] == [True, False]
    assert sorted(field.data.aliases.values()) == ["F", "T"]


def test_record_booleans_list_with_empty_aliases_skips_invalid_aliases() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.BOOLEAN, cardinality=Cardinality.LIST, include_aliases=True)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed={
            "items": [
                {"value": True, "alias": "ValidAlias"},
                {"value": False, "alias": ""},
                {"value": True, "alias": "   "},
                {"value": False, "alias": "AnotherValid"},
            ]
        },
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    field = edata.get(query.code)
    assert field is not None
    assert [el.value.mapped_value for el in field.data.elements] == [True, False, True, False]
    assert sorted(field.data.aliases.values()) == ["AnotherValid", "ValidAlias"]


def test_field_data_factory_create_boolean_list_with_empty_alias_raises_error() -> None:
    factory = FieldDataFactory()

    element1 = factory.create_checkbox(value=CheckboxValue.create(True))
    element2 = factory.create_checkbox(value=CheckboxValue.create(False))

    with pytest.raises(RuntimeError, match="Alias for element.*can't be added"):
        factory.create_generic_list(
            elements=[element1, element2],
            aliases={element1.id: "", element2.id: "ValidAlias"},
        )


def test_record_key_value_pairs_list_with_aliases_adds_aliases() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.KEY_VALUE_PAIR, cardinality=Cardinality.LIST, include_aliases=True)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed=KeyValuePairsListWithAliasesResponse(
            items=[
                KeyValuePairItemWithAlias(reasoning="r1", key="k1", value="v1", alias="A1"),
                KeyValuePairItemWithAlias(reasoning="r2", key="k2", value="v2", alias="A2"),
            ]
        ),
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    field = edata.get(query.code)
    assert field is not None
    assert [{"key": kv.key.value, "value": kv.value.value} for kv in field.data.elements] == [
        {"key": "k1", "value": "v1"},
        {"key": "k2", "value": "v2"},
    ]
    assert sorted(field.data.aliases.values()) == ["A1", "A2"]


def test_record_key_value_pairs_list_with_empty_aliases_skips_invalid_aliases() -> None:
    query = QueryFactory.create(
        shape=DataShape(data_type=DataType.KEY_VALUE_PAIR, cardinality=Cardinality.LIST, include_aliases=True)
    )
    edata = ExtractedDataFactory.make_extracted_data(document_id=123)
    resp = _Resp(
        content="{}",
        parsed={
            "items": [
                {"key": "k1", "value": "v1", "alias": "ValidAlias"},
                {"key": "k2", "value": "v2", "alias": ""},
                {"key": "k3", "value": "v3", "alias": "   "},
                {"key": "k4", "value": "v4", "alias": "AnotherValid"},
            ]
        },
    )

    InsightsRecorder().record_insights(edata, query, resp)  # type: ignore[arg-type]

    field = edata.get(query.code)
    assert field is not None
    assert [{"key": kv.key.value, "value": kv.value.value} for kv in field.data.elements] == [
        {"key": "k1", "value": "v1"},
        {"key": "k2", "value": "v2"},
        {"key": "k3", "value": "v3"},
        {"key": "k4", "value": "v4"},
    ]
    assert sorted(field.data.aliases.values()) == ["AnotherValid", "ValidAlias"]


def test_field_data_factory_create_key_value_pair_list_with_empty_alias_raises_error() -> None:
    factory = FieldDataFactory()

    key1 = factory.create_string(value="key1")
    value1 = factory.create_string(value="value1")
    kvp1 = factory.create_key_value_pair(key=key1, value=value1)

    key2 = factory.create_string(value="key2")
    value2 = factory.create_string(value="value2")
    kvp2 = factory.create_key_value_pair(key=key2, value=value2)

    with pytest.raises(RuntimeError, match="Alias for element.*can't be added"):
        factory.create_generic_list(
            elements=[kvp1, kvp2],
            aliases={kvp1.id: "", kvp2.id: "ValidAlias"},
        )
