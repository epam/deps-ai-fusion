from typing import Self

from deps_extracted_data.model import MAX_ALIAS_LENGTH
from deps_gen_ai.common import LLMResponse
from pydantic import Field, field_validator

from .base import ConfiguredBaseResponseModel
from .scalars import BooleanResponse, KeyValuePairResponse, StringResponse
from .types import BooleanWithAlias, RawKeyValuePairWithAlias, StringWithAlias

__all__ = [
    "StringsListWithAliasesResponse",
    "BooleansListWithAliasesResponse",
    "KeyValuePairsListWithAliasesResponse",
]


class _AliasMixin(ConfiguredBaseResponseModel):
    alias: str = Field(..., description="A concise label or name for this specific element in the list.")

    @field_validator("alias", mode="after")
    @classmethod
    def _truncate_alias_field(cls, alias: str) -> str:
        if len(alias) > MAX_ALIAS_LENGTH:
            return f"{alias[: MAX_ALIAS_LENGTH - 3]}..."

        return alias


class StringItemWithAlias(StringResponse, _AliasMixin):
    ...


class BooleanItemWithAlias(BooleanResponse, _AliasMixin):
    ...


class KeyValuePairItemWithAlias(KeyValuePairResponse, _AliasMixin):
    alias: str = Field(..., description="A concise label or name for this specific key-value pair.")


class StringsListWithAliasesResponse(ConfiguredBaseResponseModel):
    items: list[StringItemWithAlias] = Field(
        ...,
        description="Ordered list of string items, each with an alias.",
    )

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> list[StringWithAlias]:
        if not response.success:
            return [{"value": response.content, "alias": "Error occurred..."}]

        if response.parsed and isinstance(response.parsed, StringsListWithAliasesResponse):
            return [{"value": item.value, "alias": item.alias} for item in response.parsed.items]
        if response.parsed and isinstance(response.parsed, dict):
            return [
                {"value": str(raw_response.get("value", "")), "alias": str(raw_response.get("alias", ""))}
                for raw_response in response.parsed.get("items", [])
            ]

        return []


class BooleansListWithAliasesResponse(ConfiguredBaseResponseModel):
    items: list[BooleanItemWithAlias] = Field(
        ...,
        description="Ordered list of boolean items, each with an alias.",
    )

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> list[BooleanWithAlias]:
        if not response.success:
            return [{"value": None, "alias": "Error occurred..."}]

        if response.parsed and isinstance(response.parsed, BooleansListWithAliasesResponse):
            return [{"value": item.value, "alias": item.alias} for item in response.parsed.items]
        if response.parsed and isinstance(response.parsed, dict):
            return [
                {"value": raw_response.get("value", False), "alias": str(raw_response.get("alias", ""))}
                for raw_response in response.parsed.get("items", [])
            ]

        return []


class KeyValuePairsListWithAliasesResponse(ConfiguredBaseResponseModel):
    items: list[KeyValuePairItemWithAlias] = Field(
        ...,
        description="Ordered list of key/value pairs, each with an alias.",
    )

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> list[RawKeyValuePairWithAlias]:
        if not response.success:
            return [{"key": "Error:", "value": response.content, "alias": "Error occurred..."}]

        if response.parsed and isinstance(response.parsed, KeyValuePairsListWithAliasesResponse):
            return [{"key": item.key, "value": item.value, "alias": item.alias} for item in response.parsed.items]
        if response.parsed and isinstance(response.parsed, dict):
            return [
                {
                    "key": str(raw_response.get("key", "")),
                    "value": str(raw_response.get("value", "")),
                    "alias": str(raw_response.get("alias", "")),
                }
                for raw_response in response.parsed.get("items", [])
            ]

        return []
