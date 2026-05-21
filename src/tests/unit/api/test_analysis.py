from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from deps_ai_fusion.api.serializers.analysis import AvailableModelsResponse
from deps_ai_fusion.application import AnalysisService
from deps_ai_fusion.constants import V1_API_PREFIX
from tests.fakes import FakeFileStorage, FakeProvidersAggregate


class TestAnalysis:
    endpoint = V1_API_PREFIX + "/analysis"

    def test_insights_retrival__success(
        self,
        fake_providers_aggregate: FakeProvidersAggregate,
        authenticated_client: TestClient,
        raw_retrieve_insights_request: dict[str, Any],
    ) -> None:
        fake_llm_response = "something"
        fake_providers_aggregate.set_response(fake_llm_response)

        response = authenticated_client.post(
            f"{self.endpoint}/retrieve-insights",
            json=raw_retrieve_insights_request,
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert {code: insight["content"] for code, insight in response_data["elements"].items()} == {
            code: fake_llm_response for code in raw_retrieve_insights_request["requestedInsights"]
        }

    def test_file_insights_retrival__success(
        self,
        fake_providers_aggregate: FakeProvidersAggregate,
        authenticated_client: TestClient,
        fake_file_storage: FakeFileStorage,
        raw_retrieve_insights_request: dict[str, Any],
    ) -> None:
        fake_llm_response = "something"
        fake_providers_aggregate.set_response(fake_llm_response)
        fake_file_storage.set_bytes_response(b"some-random-bytes")

        response = authenticated_client.post(
            f"{self.endpoint}/retrieve-file-insights",
            json=raw_retrieve_insights_request,
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert {code: insight["content"] for code, insight in response_data["elements"].items()} == {
            code: fake_llm_response for code in raw_retrieve_insights_request["requestedInsights"]
        }

    @pytest.mark.parametrize(
        "invalid_field_name,invalid_value",
        [
            ("model", "provider@mod@and"),
            ("params", {"temperature": -1}),
            ("params", {"temperature": 5}),
            ("params", {"top_p": -1}),
            ("params", {"top_p": 5}),
            ("params", {"groupingFactor": 0}),
            ("params", {"groupingFactor": -1}),
        ],
    )
    def test_insights_retrival__request_validation_failure(
        self,
        fake_providers_aggregate: FakeProvidersAggregate,
        fake_file_storage: FakeFileStorage,
        authenticated_client: TestClient,
        raw_retrieve_insights_request: dict[str, Any],
        invalid_field_name: str,
        invalid_value: Any,
    ) -> None:
        fake_llm_response = "something"
        fake_providers_aggregate.set_response(fake_llm_response)

        raw_retrieve_insights_request.update({invalid_field_name: invalid_value})

        response = authenticated_client.post(
            f"{self.endpoint}/retrieve-insights",
            json=raw_retrieve_insights_request,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = authenticated_client.post(
            f"{self.endpoint}/retrieve-file-insights",
            json=raw_retrieve_insights_request,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_available_models__ok(
        self,
        fake_providers_aggregate: FakeProvidersAggregate,
        authenticated_client: TestClient,
        analysis_service: AnalysisService,
    ) -> None:
        expected_response_data = AvailableModelsResponse.from_dto(analysis_service.get_available_models()).model_dump(
            mode="json", by_alias=True
        )

        response = authenticated_client.get(f"{self.endpoint}/models")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert response_data == expected_response_data
