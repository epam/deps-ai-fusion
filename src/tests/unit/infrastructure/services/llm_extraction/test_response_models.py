from dataclasses import dataclass
from typing import Any, cast

from deps_ai_fusion.infrastructure.services.llm_extraction import (
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
from deps_ai_fusion.infrastructure.services.llm_extraction.genai_query_factory.response_models.aliases import (
    BooleanItemWithAlias,
    KeyValuePairItemWithAlias,
    StringItemWithAlias,
)


@dataclass
class _Response:
    content: str
    success: bool = True
    confidence: float | None = None
    parsed: Any | None = None


def test_string_response_parse__success_from_model() -> None:
    model = StringResponse(reasoning="r", value="v")
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert StringResponse.parse_llm_response(cast(Any, resp)) == "v"


def test_string_response_parse__success_from_dict() -> None:
    resp = _Response(content="ignored", parsed={"value": "vv"})
    assert StringResponse.parse_llm_response(cast(Any, resp)) == "vv"


def test_string_response_parse__failure_returns_content() -> None:
    resp = _Response(content="fallback", success=False)
    assert StringResponse.parse_llm_response(cast(Any, resp)) == "fallback"


def test_boolean_response_parse__success_from_model() -> None:
    model = BooleanResponse(reasoning="r", value=True)
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert BooleanResponse.parse_llm_response(cast(Any, resp)) is True


def test_boolean_response_parse__success_from_dict() -> None:
    resp = _Response(content="ignored", parsed={"value": False})
    assert BooleanResponse.parse_llm_response(cast(Any, resp)) is False


def test_boolean_response_parse__failure_returns_none() -> None:
    resp = _Response(content="x", success=False)
    assert BooleanResponse.parse_llm_response(cast(Any, resp)) is None


def test_kv_pair_response_parse__success_from_model() -> None:
    model = KeyValuePairResponse(reasoning="r", key="k", value="v")
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert KeyValuePairResponse.parse_llm_response(cast(Any, resp)) == {"key": "k", "value": "v"}


def test_kv_pair_response_parse__success_from_dict() -> None:
    resp = _Response(content="ignored", parsed={"key": "kk", "value": "vv"})
    assert KeyValuePairResponse.parse_llm_response(cast(Any, resp)) == {"key": "kk", "value": "vv"}


def test_kv_pair_response_parse__failure_returns_error_and_content() -> None:
    resp = _Response(content="err-content", success=False)
    assert KeyValuePairResponse.parse_llm_response(cast(Any, resp)) == {
        "key": "Error occurred...",
        "value": "err-content",
    }


def test_strings_list_parse() -> None:
    model = StringsListResponse(
        values=[StringResponse(reasoning="r1", value="a"), StringResponse(reasoning="r2", value="b")]
    )
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert StringsListResponse.parse_llm_response(cast(Any, resp)) == ["a", "b"]


def test_strings_list_parse__dict() -> None:
    resp = _Response(content="x", parsed={"values": [{"value": "a"}, {"value": "b"}]})
    assert StringsListResponse.parse_llm_response(cast(Any, resp)) == ["a", "b"]


def test_booleans_list_parse() -> None:
    model = BooleansListResponse(
        values=[BooleanResponse(reasoning="r1", value=True), BooleanResponse(reasoning="r2", value=False)]
    )
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert BooleansListResponse.parse_llm_response(cast(Any, resp)) == [True, False]


def test_booleans_list_parse__dict() -> None:
    resp = _Response(content="x", parsed={"values": [{"value": True}, {"value": False}]})
    assert BooleansListResponse.parse_llm_response(cast(Any, resp)) == [True, False]


def test_key_value_pairs_list_parse() -> None:
    model = KeyValuePairsListResponse(
        items=[
            KeyValuePairResponse(reasoning="r1", key="k1", value="v1"),
            KeyValuePairResponse(reasoning="r2", key="k2", value="v2"),
        ]
    )
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert KeyValuePairsListResponse.parse_llm_response(cast(Any, resp)) == [
        {"key": "k1", "value": "v1"},
        {"key": "k2", "value": "v2"},
    ]


def test_key_value_pairs_list_parse__dict() -> None:
    resp = _Response(content="x", parsed={"items": [{"key": "k1", "value": "v1"}, {"key": "k2", "value": "v2"}]})
    assert KeyValuePairsListResponse.parse_llm_response(cast(Any, resp)) == [
        {"key": "k1", "value": "v1"},
        {"key": "k2", "value": "v2"},
    ]


def test_strings_list_with_aliases_parse() -> None:
    model = StringsListWithAliasesResponse(
        items=[
            StringItemWithAlias(reasoning="r1", value="a", alias="A"),
            StringItemWithAlias(reasoning="r2", value="b", alias="B"),
        ]
    )
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert StringsListWithAliasesResponse.parse_llm_response(cast(Any, resp)) == [
        {"value": "a", "alias": "A"},
        {"value": "b", "alias": "B"},
    ]


def test_booleans_list_with_aliases_parse() -> None:
    model = BooleansListWithAliasesResponse(
        items=[
            BooleanItemWithAlias(reasoning="r1", value=True, alias="T"),
            BooleanItemWithAlias(reasoning="r2", value=False, alias="F"),
        ]
    )
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert BooleansListWithAliasesResponse.parse_llm_response(cast(Any, resp)) == [
        {"value": True, "alias": "T"},
        {"value": False, "alias": "F"},
    ]


def test_key_value_pairs_with_aliases_parse() -> None:
    model = KeyValuePairsListWithAliasesResponse(
        items=[
            KeyValuePairItemWithAlias(reasoning="r1", key="k1", value="v1", alias="A1"),
            KeyValuePairItemWithAlias(reasoning="r2", key="k2", value="v2", alias="A2"),
        ]
    )
    resp = _Response(content=model.model_dump_json(), parsed=model)
    assert KeyValuePairsListWithAliasesResponse.parse_llm_response(cast(Any, resp)) == [
        {"key": "k1", "value": "v1", "alias": "A1"},
        {"key": "k2", "value": "v2", "alias": "A2"},
    ]


def test_strings_list_with_aliases_parse__failure_returns_error_placeholder() -> None:
    resp = _Response(content="err-content", success=False)
    assert StringsListWithAliasesResponse.parse_llm_response(cast(Any, resp)) == [
        {"value": "err-content", "alias": "Error occurred..."},
    ]


def test_booleans_list_with_aliases_parse__failure_returns_error_placeholder() -> None:
    resp = _Response(content="err-content", success=False)
    assert BooleansListWithAliasesResponse.parse_llm_response(cast(Any, resp)) == [
        {"value": None, "alias": "Error occurred..."},
    ]


def test_key_value_pairs_list_with_aliases_parse__failure_returns_error_placeholder() -> None:
    resp = _Response(content="err-content", success=False)
    assert KeyValuePairsListWithAliasesResponse.parse_llm_response(cast(Any, resp)) == [
        {"key": "Error:", "value": "err-content", "alias": "Error occurred..."},
    ]
