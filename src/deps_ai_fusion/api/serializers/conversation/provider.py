from deps_gen_ai.common import LLM, ContextType, Provider
from pydantic import Field

from ..base import ConfiguredBaseModel

__all__ = ["SerializedProvider", "SerializedLLM"]


class SerializedLLM(ConfiguredBaseModel):
    code: str
    name: str
    context_type: ContextType = Field(..., alias="contextType")
    description: str

    @classmethod
    def from_dto(cls, model: LLM) -> "SerializedLLM":
        return cls(
            code=model.code,
            name=model.name,
            description=model.description,
            context_type=model.context_type,
        )


class SerializedProvider(ConfiguredBaseModel):
    code: str
    name: str
    models: list[SerializedLLM]

    @classmethod
    def from_objects(cls, provider: Provider, models: list[LLM]) -> "SerializedProvider":
        return cls(
            code=provider.code,
            name=provider.name,
            models=[SerializedLLM.from_dto(model) for model in models],
        )
