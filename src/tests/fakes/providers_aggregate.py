import re

from deps_gen_ai.common import (
    LLM,
    ContextType,
    LLMResponse,
    PageSpan,
    Provider,
    Query,
    RetrievedInsights,
)
from deps_gen_ai.exceptions import ProviderNotFound
from deps_gen_ai.providers_aggregate import ProvidersAggregate

__all__ = ["FakeProvidersAggregate"]


class FakeProvidersAggregate(ProvidersAggregate):
    def __init__(self) -> None:
        self._response: LLMResponse | None = None
        self.providers = [Provider(code="dial", name="Epam DIAL")]
        self.models = {
            "dial": [
                LLM(
                    code="dial",
                    name="GPT",
                    context_type=ContextType.TEXT_BASED,
                    vendor_code_regex=re.compile(""),
                    legacy=False,
                ),
                LLM(
                    code="dial",
                    name="GPT-2",
                    context_type=ContextType.TEXT_BASED,
                    vendor_code_regex=re.compile(""),
                    legacy=False,
                ),
                LLM(
                    code="dial",
                    name="GPT-3",
                    context_type=ContextType.TEXT_BASED,
                    vendor_code_regex=re.compile(""),
                    legacy=True,
                ),
            ],
        }
        self._insights_retrival_request_made_with: tuple[str, str] | None = None

    def set_response(self, response: str, confidence: float | None = None) -> None:
        self._response = LLMResponse(content=response, confidence=confidence)

    def chat_request(self, *args, **kwargs) -> LLMResponse:
        if self._response is None:
            raise RuntimeError("No response set for FakeProvidersAggregate")
        return self._response

    def retrieve_insights(
        self,
        provider: str,
        model: str,
        entity_id: str,
        elements: dict[str, Query],
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        seed: int | None = None,
        custom_instructions: str | None = None,
        retrival_group_size: int | None = None,
        page_span: PageSpan | None = None,
        files: list[str] | None = None,
    ) -> RetrievedInsights:
        self._insights_retrival_request_made_with = (provider, model)

        if self._response is None:
            raise RuntimeError("No response set for FakeProvidersAggregate")
        return RetrievedInsights(insights={element_code: self._response for element_code in elements.keys()})

    def retrieve_file_insights(
        self,
        provider: str,
        model: str,
        filepath: str,
        file_blob: bytes,
        elements: dict[str, Query],
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        seed: int | None = None,
        custom_instructions: str | None = None,
        retrival_group_size: int | None = None,
        page_span: PageSpan | None = None,
        files: list[str] | None = None,
    ) -> RetrievedInsights:
        self._insights_retrival_request_made_with = (provider, model)

        if self._response is None:
            raise RuntimeError("No response set for FakeProvidersAggregate")
        return RetrievedInsights(insights={element_code: self._response for element_code in elements.keys()})

    def supported_providers(self) -> list[Provider]:
        return self.providers

    def models_of(self, provider: str, include_legacy: bool = False) -> list[LLM]:
        if provider not in self.models:
            raise ProviderNotFound(provider)

        return [model for model in self.models[provider] if (include_legacy or not model.legacy)]

    def assert_insights_retrival_request_made_with(self, provider: str, model: str) -> None:
        assert self._insights_retrival_request_made_with == (provider, model)
        self._insights_retrival_request_made_with = None
