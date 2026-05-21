from typing import Self

from deps_gen_ai.common import LLMResponse
from pydantic import Field

from .base import ConfiguredBaseResponseModel
from .scalars import BooleanResponse, KeyValuePairResponse, StringResponse
from .types import RawKeyValuePair

__all__ = [
    "StringsListResponse",
    "BooleansListResponse",
    "KeyValuePairsListResponse",
]


class StringsListResponse(ConfiguredBaseResponseModel):
    values: list[StringResponse] = Field(
        ...,
        description="Ordered list of extracted string values.",
    )

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> list[str]:
        if not response.success:
            return [response.content]

        if response.parsed and isinstance(response.parsed, StringsListResponse):
            return [response.value for response in response.parsed.values]
        if response.parsed and isinstance(response.parsed, dict):
            return [str(raw_response.get("value", "")) for raw_response in response.parsed.get("values", [])]

        return []


class BooleansListResponse(ConfiguredBaseResponseModel):
    values: list[BooleanResponse] = Field(
        ...,
        description="Ordered list of extracted boolean values.",
    )

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> list[bool]:
        if not response.success:
            return []

        if response.parsed and isinstance(response.parsed, BooleansListResponse):
            return [response.value for response in response.parsed.values]
        if response.parsed and isinstance(response.parsed, dict):
            return [raw_response.get("value", False) for raw_response in response.parsed.get("values", [])]

        return []


class KeyValuePairsListResponse(ConfiguredBaseResponseModel):
    items: list[KeyValuePairResponse] = Field(
        ...,
        description="Ordered list of key/value pairs.",
    )

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> list[RawKeyValuePair]:
        if not response.success:
            return [{"key": "Error:", "value": response.content}]

        if response.parsed and isinstance(response.parsed, KeyValuePairsListResponse):
            return [{"key": item.key, "value": item.value} for item in response.parsed.items]
        if response.parsed and isinstance(response.parsed, dict):
            return [
                {"key": str(raw_response.get("key", "")), "value": str(raw_response.get("value", ""))}
                for raw_response in response.parsed.get("items", [])
            ]

        return []
