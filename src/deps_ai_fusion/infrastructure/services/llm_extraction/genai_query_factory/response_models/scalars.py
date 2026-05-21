from typing import Self

from deps_gen_ai.common import LLMResponse
from pydantic import Field

from .base import ConfiguredBaseResponseModel
from .types import RawKeyValuePair

__all__ = [
    "StringResponse",
    "BooleanResponse",
    "KeyValuePairResponse",
]


class StringResponse(ConfiguredBaseResponseModel):
    reasoning: str = Field(
        ...,
        description="Step-by-step explanation on how and why this value was selected from the context.",
    )
    value: str = Field(..., description="The extracted string value.")

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> str:
        if not response.success:
            return response.content

        if response.parsed and isinstance(response.parsed, StringResponse):
            return response.parsed.value
        if response.parsed and isinstance(response.parsed, dict):
            return str(response.parsed.get("value", response.content))

        return response.content


class BooleanResponse(ConfiguredBaseResponseModel):
    reasoning: str = Field(
        ...,
        description="Step-by-step explanation on how and why this value was selected from the context.",
    )
    value: bool = Field(..., description="The extracted boolean value.")

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> bool | None:
        if not response.success:
            return None

        if response.parsed and isinstance(response.parsed, BooleanResponse):
            return response.parsed.value
        if response.parsed and isinstance(response.parsed, dict):
            return response.parsed.get("value", None)

        return None


class KeyValuePairResponse(ConfiguredBaseResponseModel):
    reasoning: str = Field(
        ...,
        description="Step-by-step explanation on how and why this key/value pair was selected from the context.",
    )
    key: str = Field(..., description="The key/name.")
    value: str = Field(..., description="The value associated with the key.")

    @classmethod
    def parse_llm_response(cls, response: LLMResponse[Self]) -> RawKeyValuePair:
        if not response.success:
            return {"key": "Error occurred...", "value": response.content}

        if response.parsed and isinstance(response.parsed, KeyValuePairResponse):
            return {"key": response.parsed.key, "value": response.parsed.value}
        if response.parsed and isinstance(response.parsed, dict):
            return {
                "key": str(response.parsed.get("key", "Error occurred...")),
                "value": str(response.parsed.get("value", response.content)),
            }

        return {"key": "Error occurred...", "value": response.content}
