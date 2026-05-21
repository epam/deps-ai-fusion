from typing_extensions import Self

from deps_ai_fusion.application.types import ProviderModels

from ..base import ConfiguredBaseModel
from ..conversation.provider import SerializedProvider

__all__ = ["AvailableModelsResponse"]


class AvailableModelsResponse(ConfiguredBaseModel):
    providers: list[SerializedProvider]

    @classmethod
    def from_dto(cls, provider_models_list: list[ProviderModels]) -> Self:
        return cls(
            providers=[
                SerializedProvider.from_objects(provider=provider_models.provider, models=provider_models.models)
                for provider_models in provider_models_list
            ],
        )
