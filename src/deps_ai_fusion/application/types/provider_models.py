from dataclasses import dataclass

from deps_gen_ai.common import LLM, Provider

__all__ = ["ProviderModels"]


@dataclass(frozen=True, slots=True)
class ProviderModels:
    provider: Provider
    models: list[LLM]
