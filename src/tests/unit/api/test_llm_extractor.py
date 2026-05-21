import json
import random
from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from deps_ai_fusion.constants import V1_API_PREFIX
from deps_ai_fusion.domain.model import (
    ContextAttachments,
    ILLMExtractorRepository,
    LLMExtractor,
    Query,
)


def test_add_query__created(
    raw_query_with_single_node_request_factory,
    llm_extractor: LLMExtractor,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    fake_llm_extractor_repository.save(llm_extractor)

    url = f"{V1_API_PREFIX}/document-types/{llm_extractor.document_type_id()}/llm-extractors/{llm_extractor.id()}/query"
    raw_query_request = raw_query_with_single_node_request_factory()
    response = authenticated_client.post(url, json=raw_query_request)

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data["code"] == raw_query_request["code"]
    assert response_data["shape"]["cardinality"] == raw_query_request["shape"]["cardinality"]
    assert response_data["shape"]["dataType"] == raw_query_request["shape"]["dataType"]
    assert response_data["shape"]["includeAliases"] == raw_query_request["shape"]["includeAliases"]
    assert response_data["workflow"]["startNodeId"] == raw_query_request["workflow"]["startNodeId"]
    assert response_data["workflow"]["endNodeId"] == raw_query_request["workflow"]["endNodeId"]

    for node, orig_node in zip(response_data["workflow"]["nodes"], raw_query_request["workflow"]["nodes"]):
        assert node["id"] == orig_node["id"]
        assert node["name"] == orig_node["name"]
        assert node["prompt"] == orig_node["prompt"]

    for edge, orig_edge in zip(response_data["workflow"]["edges"], raw_query_request["workflow"]["edges"]):
        assert edge["sourceId"] == orig_edge["sourceId"]
        assert edge["targetId"] == orig_edge["targetId"]


def test_add_query__not_found(
    raw_query_with_single_node_request_factory,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    url = f"{V1_API_PREFIX}/document-types/fake-doctype-id/llm-extractors/fake-extractor-id/query"
    raw_query_request = raw_query_with_single_node_request_factory()

    response = authenticated_client.post(url, json=raw_query_request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_query__conflict(
    raw_query_with_single_node_request_factory,
    llm_extractor_with_query: LLMExtractor,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    fake_llm_extractor_repository.save(llm_extractor_with_query)

    url = (
        f"{V1_API_PREFIX}/document-types/{llm_extractor_with_query.document_type_id()}"
        f"/llm-extractors/{llm_extractor_with_query.id()}/query"
    )
    existing_query = llm_extractor_with_query.query_values()[0]
    raw_query_request = raw_query_with_single_node_request_factory(
        code=existing_query.code,
        node_id=existing_query.workflow.nodes[0].id,
    )

    response = authenticated_client.post(url, json=raw_query_request)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_query__ok(
    raw_query_with_single_node_request_factory,
    llm_extractor_with_query: LLMExtractor,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    fake_llm_extractor_repository.save(llm_extractor_with_query)

    query_for_update = llm_extractor_with_query.query_values()[0]
    updated_workflow = raw_query_with_single_node_request_factory()["workflow"]

    url = (
        f"{V1_API_PREFIX}/document-types/{llm_extractor_with_query.document_type_id()}/"
        f"llm-extractors/{llm_extractor_with_query.id()}/query/{query_for_update.code}"
    )

    response = authenticated_client.patch(url, json={"workflow": updated_workflow})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data["code"] == query_for_update.code
    assert response_data["shape"]["cardinality"] == query_for_update.shape.cardinality
    assert response_data["shape"]["dataType"] == query_for_update.shape.data_type
    assert response_data["shape"]["includeAliases"] == query_for_update.shape.include_aliases
    assert response_data["workflow"]["startNodeId"] == updated_workflow["startNodeId"]
    assert response_data["workflow"]["endNodeId"] == updated_workflow["endNodeId"]

    for node, orig_node in zip(response_data["workflow"]["nodes"], updated_workflow["nodes"]):
        assert node["id"] == orig_node["id"]
        assert node["name"] == orig_node["name"]
        assert node["prompt"] == orig_node["prompt"]

    for edge, orig_edge in zip(response_data["workflow"]["edges"], updated_workflow["edges"]):
        assert edge["sourceId"] == orig_edge["sourceId"]
        assert edge["targetId"] == orig_edge["targetId"]


@pytest.mark.parametrize(
    "prompt_value",
    [
        [""],
        ["       "],
    ],
)
def test_update_prompt__unprocessable_content(
    raw_query_with_single_node_request_factory,
    prompt_value: str,
    llm_extractor_with_query: LLMExtractor,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    fake_llm_extractor_repository.save(llm_extractor_with_query)
    query_for_update = llm_extractor_with_query.query_values()[0]
    updated_workflow = raw_query_with_single_node_request_factory(prompt=prompt_value)["workflow"]

    url = (
        f"{V1_API_PREFIX}/document-types/{llm_extractor_with_query.document_type_id()}"
        f"/llm-extractors/{llm_extractor_with_query.id()}/query/{query_for_update.code}"
    )

    response = authenticated_client.patch(url, json={"workflow": updated_workflow})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_query__not_found(
    raw_query_with_single_node_request_factory,
    llm_extractor_factory: LLMExtractor,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    llm_extractor = llm_extractor_factory(queries={})
    fake_llm_extractor_repository.save(llm_extractor)
    updated_query = raw_query_with_single_node_request_factory()

    url = (
        f"{V1_API_PREFIX}/document-types/{llm_extractor.document_type_id()}"
        f"/llm-extractors/{llm_extractor.id()}/query/{updated_query['code']}"
    )

    response = authenticated_client.patch(url, json={"workflow": updated_query["workflow"]})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_extractor__ok(
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor: LLMExtractor,
    authenticated_client: TestClient,
):
    token = json.loads(authenticated_client.headers.get("deps-token", "{}"))
    fake_llm_extractor_repository.save(llm_extractor)

    url = f"{V1_API_PREFIX}/document-types/{llm_extractor.document_type_id()}/llm-extractors/{llm_extractor.id()}"
    data = {
        "name": "new_name",
        "extractionParams": {
            "customInstruction": "new_instruction",
            "groupingFactor": 3,
            "temperature": 0.5,
            "topP": 0.1,
            "pageSpan": {"start": 5, "end": 20},
        },
    }

    response = authenticated_client.put(url, json=data)
    assert response.status_code == status.HTTP_200_OK

    updated_llm_extractor = fake_llm_extractor_repository.find_for_document_type(
        id_=llm_extractor.id(),
        document_type_id=llm_extractor.document_type_id(),
        tenant_id=token.get("organisation"),
    )
    assert updated_llm_extractor is not None
    assert updated_llm_extractor.name == data["name"]
    assert updated_llm_extractor.extraction_params.custom_instruction == data["extractionParams"]["customInstruction"]  # type: ignore
    assert updated_llm_extractor.extraction_params.grouping_factor == data["extractionParams"]["groupingFactor"]  # type: ignore
    assert updated_llm_extractor.extraction_params.temperature == data["extractionParams"]["temperature"]  # type: ignore
    assert updated_llm_extractor.extraction_params.top_p == data["extractionParams"]["topP"]  # type: ignore
    assert updated_llm_extractor.extraction_params.page_span.start == data["extractionParams"]["pageSpan"]["start"]  # type: ignore
    assert updated_llm_extractor.extraction_params.page_span.end == data["extractionParams"]["pageSpan"]["end"]  # type: ignore


def test_update_extractor__with_page_span__error(
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor: LLMExtractor,
    authenticated_client: TestClient,
):
    fake_llm_extractor_repository.save(llm_extractor)

    url = f"{V1_API_PREFIX}/document-types/{llm_extractor.document_type_id()}/llm-extractors/{llm_extractor.id()}"
    data = {
        "name": llm_extractor.name,
        "extractionParams": {
            "customInstruction": llm_extractor.extraction_params.custom_instruction,
            "groupingFactor": llm_extractor.extraction_params.grouping_factor,
            "temperature": llm_extractor.extraction_params.temperature,
            "topP": llm_extractor.extraction_params.top_p,
            "pageSpan": {"start": 5, "end": 3},
        },
    }

    response = authenticated_client.put(url, json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_extrator__update_page_span_from_value_to_none__ok(
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor: LLMExtractor,
    authenticated_client: TestClient,
):
    token = json.loads(authenticated_client.headers.get("deps-token", "{}"))
    fake_llm_extractor_repository.save(llm_extractor)

    url = f"{V1_API_PREFIX}/document-types/{llm_extractor.document_type_id()}/llm-extractors/{llm_extractor.id()}"
    data = {
        "name": llm_extractor.name,
        "extractionParams": {
            "customInstruction": llm_extractor.extraction_params.custom_instruction,
            "groupingFactor": llm_extractor.extraction_params.grouping_factor,
            "temperature": llm_extractor.extraction_params.temperature,
            "topP": llm_extractor.extraction_params.top_p,
            "pageSpan": None,
        },
    }

    response = authenticated_client.put(url, json=data)
    assert response.status_code == status.HTTP_200_OK

    updated_llm_extractor = fake_llm_extractor_repository.find_for_document_type(
        id_=llm_extractor.id(),
        document_type_id=llm_extractor.document_type_id(),
        tenant_id=token.get("organisation"),
    )
    assert updated_llm_extractor.extraction_params.page_span is None


def test_update_extrator__update_page_span_from_none_to_value__ok(
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor__no_page_span: LLMExtractor,
    authenticated_client: TestClient,
):
    token = json.loads(authenticated_client.headers.get("deps-token", "{}"))
    fake_llm_extractor_repository.save(llm_extractor__no_page_span)

    url = f"{V1_API_PREFIX}/document-types/{llm_extractor__no_page_span.document_type_id()}/llm-extractors/{llm_extractor__no_page_span.id()}"
    data = {
        "name": llm_extractor__no_page_span.name,
        "extractionParams": {
            "customInstruction": llm_extractor__no_page_span.extraction_params.custom_instruction,
            "groupingFactor": llm_extractor__no_page_span.extraction_params.grouping_factor,
            "temperature": llm_extractor__no_page_span.extraction_params.temperature,
            "topP": llm_extractor__no_page_span.extraction_params.top_p,
            "pageSpan": {"start": 3, "end": 5},
        },
    }

    response = authenticated_client.put(url, json=data)
    assert response.status_code == status.HTTP_200_OK

    updated_llm_extractor = fake_llm_extractor_repository.find_for_document_type(
        id_=llm_extractor__no_page_span.id(),
        document_type_id=llm_extractor__no_page_span.document_type_id(),
        tenant_id=token.get("organisation"),
    )
    assert updated_llm_extractor.extraction_params.page_span.start == data["extractionParams"]["pageSpan"]["start"]
    assert updated_llm_extractor.extraction_params.page_span.end == data["extractionParams"]["pageSpan"]["end"]


def test_update_extractor__not_found(
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor: LLMExtractor,
    authenticated_client: TestClient,
):
    url = f"{V1_API_PREFIX}/document-types/random_id/llm-extractors/random_id"
    data = {
        "name": "new_name",
        "extractionParams": {
            "customInstruction": "new_instruction",
            "groupingFactor": 3,
            "temperature": 0.5,
            "topP": 0.1,
            "pageSpan": {"start": 5, "end": 20},
        },
    }

    response = authenticated_client.put(url, json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_llm_extractors__ok(
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor_with_query: LLMExtractor,
    authenticated_client: TestClient,
):
    url = f"{V1_API_PREFIX}/document-types/{llm_extractor_with_query.document_type_id()}/llm-extractors"

    fake_llm_extractor_repository.save(llm_extractor_with_query)

    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    llm_extractors = response.json()["llmExtractors"]

    assert len(llm_extractors) == 1

    ext = llm_extractors[0]

    assert ext["extractorId"] == llm_extractor_with_query.id()
    assert ext["name"] == llm_extractor_with_query.name
    assert ext["llmReference"]["provider"] == llm_extractor_with_query.llm_reference.provider
    assert ext["llmReference"]["model"] == llm_extractor_with_query.llm_reference.model

    extraction_params = ext["extractionParams"]

    assert extraction_params["customInstruction"] == llm_extractor_with_query.extraction_params.custom_instruction
    assert extraction_params["groupingFactor"] == llm_extractor_with_query.extraction_params.grouping_factor
    assert extraction_params["temperature"] == llm_extractor_with_query.extraction_params.temperature
    assert extraction_params["topP"] == llm_extractor_with_query.extraction_params.top_p

    assert len(ext["queries"]) == len(llm_extractor_with_query.query_values())

    for raw_query, query in zip(ext["queries"], llm_extractor_with_query.query_values()):
        assert raw_query["code"] == query.code
        assert raw_query["shape"]["cardinality"] == query.shape.cardinality
        assert raw_query["shape"]["dataType"] == query.shape.data_type
        assert raw_query["shape"]["includeAliases"] == query.shape.include_aliases

        assert raw_query["workflow"]["startNodeId"] == query.workflow.entrypoint_node_id
        assert raw_query["workflow"]["endNodeId"] == query.workflow.output_node_id

        for raw_node, node in zip(raw_query["workflow"]["nodes"], query.workflow.nodes):
            assert raw_node["prompt"] == node.prompt
            assert raw_node["id"] == node.id
            assert raw_node["name"] == node.name

        for raw_edge, edge in zip(raw_query["workflow"]["edges"], query.workflow.edges):
            assert raw_edge["sourceId"] == edge.source_id
            assert raw_edge["targetId"] == edge.target_id


def test_create_extractor_with_context_attachments__ok(
    raw_create_llm_extractor_request_data: dict[str, Any],
    authenticated_client: TestClient,
    mock_extraction_service,
):
    mock_extraction_service.create_extractor.return_value = ("document_type_id", "extractor_id")

    url = f"{V1_API_PREFIX}/document-types/llm-extractors"

    response = authenticated_client.post(url, json=raw_create_llm_extractor_request_data)

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data["extractorId"] == "extractor_id"
    assert response_data["documentTypeId"] == "document_type_id"


def test_update_extractor__update_context_attachments_from_none_to_value__ok(
    llm_extractor_no_context_attachments: LLMExtractor,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    fake_llm_extractor_repository.save(llm_extractor_no_context_attachments)

    url = f"{V1_API_PREFIX}/document-types/{llm_extractor_no_context_attachments.document_type_id()}/llm-extractors/{llm_extractor_no_context_attachments.id()}"
    data = {
        "name": llm_extractor_no_context_attachments.name,
        "extractionParams": {
            "customInstruction": llm_extractor_no_context_attachments.extraction_params.custom_instruction,
            "groupingFactor": llm_extractor_no_context_attachments.extraction_params.grouping_factor,
            "temperature": llm_extractor_no_context_attachments.extraction_params.temperature,
            "topP": llm_extractor_no_context_attachments.extraction_params.top_p,
            "pageSpan": {"start": 1, "end": 3},
            "contextAttachments": random.choice(list(ContextAttachments)),
        },
    }

    response = authenticated_client.put(url, json=data)
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data["extractorId"] == llm_extractor_no_context_attachments.id.value
    assert response_data["documentTypeId"] == llm_extractor_no_context_attachments.document_type_id.value


def test_update_extractor__update_context_attachments_from_value_to_none__ok(
    llm_extractor: LLMExtractor,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    authenticated_client: TestClient,
):
    fake_llm_extractor_repository.save(llm_extractor)

    url = f"{V1_API_PREFIX}/document-types/{llm_extractor.document_type_id()}/llm-extractors/{llm_extractor.id()}"
    data = {
        "name": llm_extractor.name,
        "extractionParams": {
            "customInstruction": llm_extractor.extraction_params.custom_instruction,
            "groupingFactor": llm_extractor.extraction_params.grouping_factor,
            "temperature": llm_extractor.extraction_params.temperature,
            "topP": llm_extractor.extraction_params.top_p,
            "pageSpan": {"start": 1, "end": 3},
            "contextAttachments": None,
        },
    }

    response = authenticated_client.put(url, json=data)
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data["extractorId"] == llm_extractor.id.value
    assert response_data["documentTypeId"] == llm_extractor.document_type_id.value
