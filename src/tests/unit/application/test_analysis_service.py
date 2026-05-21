from typing import Any

import pytest

from deps_ai_fusion.application import AnalysisService
from deps_ai_fusion.domain.exceptions import LLMExtractorNotFoundError
from tests.fakes import FakeFileStorage, FakeProvidersAggregate


def test_insights_retrival__success(
    fake_providers_aggregate: FakeProvidersAggregate,
    fake_file_storage: FakeFileStorage,
    analysis_service: AnalysisService,
    raw_insights_retrival_request_data: dict[str, Any],
) -> None:
    fake_llm_response = "something"
    fake_providers_aggregate.set_response(fake_llm_response)

    ri = analysis_service.retrieve_insights(
        llm_reference=raw_insights_retrival_request_data["llm_reference"],
        document_id=raw_insights_retrival_request_data["entity_id"],
        requested_insights=raw_insights_retrival_request_data["elements"],
        custom_instructions=raw_insights_retrival_request_data["custom_instructions"],
        temperature=raw_insights_retrival_request_data["temperature"],
        top_p=raw_insights_retrival_request_data["top_p"],
        retrival_group_size=raw_insights_retrival_request_data["retrival_group_size"],
        files=raw_insights_retrival_request_data["files"],
    )

    assert {code: llm_response.content for code, llm_response in ri.insights.items()} == {
        code: fake_llm_response for code in raw_insights_retrival_request_data["elements"]
    }

    ri = analysis_service.retrieve_file_insights(
        llm_reference=raw_insights_retrival_request_data["llm_reference"],
        filepath=raw_insights_retrival_request_data["filepath"],
        requested_insights=raw_insights_retrival_request_data["elements"],
        custom_instructions=raw_insights_retrival_request_data["custom_instructions"],
        temperature=raw_insights_retrival_request_data["temperature"],
        top_p=raw_insights_retrival_request_data["top_p"],
        retrival_group_size=raw_insights_retrival_request_data["retrival_group_size"],
        files=raw_insights_retrival_request_data["files"],
    )

    assert {code: llm_response.content for code, llm_response in ri.insights.items()} == {
        code: fake_llm_response for code in raw_insights_retrival_request_data["elements"]
    }


@pytest.mark.parametrize(
    "llm_reference,expected_provider,expected_model",
    [
        ("provider@model", "provider", "model"),
        ("model", AnalysisService._DEFAULT_PROVIDER, "model"),
    ],
)
def test_insights_retrival__llm_reference_default_provider(
    llm_reference: str,
    expected_provider: str,
    expected_model: str,
    fake_providers_aggregate: FakeProvidersAggregate,
    fake_file_storage: FakeFileStorage,
    analysis_service: AnalysisService,
    raw_insights_retrival_request_data: dict[str, Any],
) -> None:
    fake_providers_aggregate.set_response("something")

    analysis_service.retrieve_insights(
        llm_reference=llm_reference,
        document_id=raw_insights_retrival_request_data["entity_id"],
        requested_insights=raw_insights_retrival_request_data["elements"],
        custom_instructions=raw_insights_retrival_request_data["custom_instructions"],
        temperature=raw_insights_retrival_request_data["temperature"],
        top_p=raw_insights_retrival_request_data["top_p"],
        retrival_group_size=raw_insights_retrival_request_data["retrival_group_size"],
        files=raw_insights_retrival_request_data["files"],
    )

    fake_providers_aggregate.assert_insights_retrival_request_made_with(
        provider=expected_provider,
        model=expected_model,
    )

    analysis_service.retrieve_file_insights(
        llm_reference=llm_reference,
        filepath=raw_insights_retrival_request_data["filepath"],
        requested_insights=raw_insights_retrival_request_data["elements"],
        custom_instructions=raw_insights_retrival_request_data["custom_instructions"],
        temperature=raw_insights_retrival_request_data["temperature"],
        top_p=raw_insights_retrival_request_data["top_p"],
        retrival_group_size=raw_insights_retrival_request_data["retrival_group_size"],
        files=raw_insights_retrival_request_data["files"],
    )

    fake_providers_aggregate.assert_insights_retrival_request_made_with(
        provider=expected_provider,
        model=expected_model,
    )


def test_get_available_models__ok(
    fake_providers_aggregate: FakeProvidersAggregate,
    analysis_service: AnalysisService,
) -> None:
    provider_models_list = analysis_service.get_available_models()

    assert fake_providers_aggregate.providers == [provider_models.provider for provider_models in provider_models_list]

    for provider_models in provider_models_list:
        assert provider_models.models == fake_providers_aggregate.models_of(
            provider=provider_models.provider.code,
            include_legacy=True,
        )
