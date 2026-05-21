from typing import Protocol

from deps_ai_fusion.domain.model import LLMExtractor

__all__ = ["IControlLLMs"]


class IControlLLMs(Protocol):
    def execute_extractor(
        self,
        llm_extractor: LLMExtractor,
        document_id: str,
        override_llm: str | None = None,
    ) -> None:
        ...

    def llm_exists(self, provider: str, model: str) -> bool:
        ...
