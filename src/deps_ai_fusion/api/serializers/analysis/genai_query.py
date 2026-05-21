from typing import Any

from pydantic import Field

from ..base import ConfiguredBaseModel

__all__ = ["SerializedGenAIQuery"]


class SerializedGenAIPrompt(ConfiguredBaseModel):
    content: str


class SerializedGenAIWorkflow(ConfiguredBaseModel):
    prompts: list[SerializedGenAIPrompt]
    response_model: dict[str, Any] | None = Field(
        None,
        alias="responseModel",
        description="A JSON Schema (OpenAPI V3) object defining the shape of the LLM’s structured response..",
    )


class SerializedGenAIQuery(ConfiguredBaseModel):
    workflow: SerializedGenAIWorkflow
