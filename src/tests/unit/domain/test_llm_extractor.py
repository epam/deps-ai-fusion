import random
import uuid

import pytest
from deps_gen_ai.providers import ProviderCode

from deps_ai_fusion.domain.exceptions import QueryAlreadyExistsError, QueryNotFoundError
from deps_ai_fusion.domain.model.llm_extractor import (
    ContextAttachments,
    LLMExtractor,
    LLMExtractorFactory,
    RawDataShape,
    RawLLMExtractionParams,
    RawLLMWorkflow,
    RawPageSpan,
)


def test_llm_extractor__factory_create() -> None:
    llm_extractor = LLMExtractorFactory.create(
        id_=(id_ := uuid.uuid4().hex),
        tenant_id=(tenant_id := uuid.uuid4().hex),
        document_type_id=(document_type_id := uuid.uuid4().hex),
        provider=(provider := ProviderCode.EPAM_DIAL),
        name=(name := uuid.uuid4().hex),
        model=(model := uuid.uuid4().hex),
    )

    assert llm_extractor.id() == id_
    assert llm_extractor.tenant_id() == tenant_id
    assert llm_extractor.document_type_id() == document_type_id
    assert llm_extractor.name == name
    assert llm_extractor.llm_reference.provider == provider
    assert llm_extractor.llm_reference.model == model


def test_llm_extractor__update(llm_extractor: LLMExtractor) -> None:
    name = "HelloLLM"
    extraction_params = RawLLMExtractionParams(
        custom_instruction=uuid.uuid4().hex,
        grouping_factor=random.randint(1, 100),
        temperature=random.random(),
        top_p=random.random(),
        page_span=RawPageSpan(start=1, end=random.randint(2, 100)),
        context_attachments=None,
    )

    llm_extractor.update(
        name=name,
        params=extraction_params,
    )

    assert llm_extractor.name == name
    assert llm_extractor.extraction_params.custom_instruction == extraction_params["custom_instruction"]
    assert llm_extractor.extraction_params.grouping_factor == extraction_params["grouping_factor"]
    assert llm_extractor.extraction_params.temperature == extraction_params["temperature"]
    assert llm_extractor.extraction_params.top_p == extraction_params["top_p"]
    assert llm_extractor.extraction_params.page_span.start == extraction_params["page_span"]["start"]
    assert llm_extractor.extraction_params.page_span.end == extraction_params["page_span"]["end"]


def test_llm_extractor__update_page_span_from_value_to_none(llm_extractor):
    extraction_params = RawLLMExtractionParams(
        custom_instruction=llm_extractor.extraction_params.custom_instruction,
        grouping_factor=llm_extractor.extraction_params.grouping_factor,
        temperature=llm_extractor.extraction_params.temperature,
        top_p=llm_extractor.extraction_params.top_p,
        page_span=None,
        context_attachments=None,
    )

    llm_extractor.update(name=llm_extractor.name, params=extraction_params)

    assert llm_extractor.extraction_params.page_span == extraction_params["page_span"]


def test_llm_extractor__update_page_span_from_none_to_value(llm_extractor__no_page_span):
    extraction_params = RawLLMExtractionParams(
        custom_instruction=llm_extractor__no_page_span.extraction_params.custom_instruction,
        grouping_factor=llm_extractor__no_page_span.extraction_params.grouping_factor,
        temperature=llm_extractor__no_page_span.extraction_params.temperature,
        top_p=llm_extractor__no_page_span.extraction_params.top_p,
        page_span=RawPageSpan(start=random.randint(1, 3), end=random.randint(4, 6)),
        context_attachments=None,
    )

    llm_extractor__no_page_span.update(name=llm_extractor__no_page_span.name, params=extraction_params)

    assert llm_extractor__no_page_span.extraction_params.page_span.start == extraction_params["page_span"]["start"]
    assert llm_extractor__no_page_span.extraction_params.page_span.end == extraction_params["page_span"]["end"]


def test_llm_extractor__update_context_attachments_from_value_to_none(llm_extractor):
    extraction_params = RawLLMExtractionParams(
        custom_instruction=llm_extractor.extraction_params.custom_instruction,
        grouping_factor=llm_extractor.extraction_params.grouping_factor,
        temperature=llm_extractor.extraction_params.temperature,
        top_p=llm_extractor.extraction_params.top_p,
        page_span=None,
        context_attachments=None,
    )

    llm_extractor.update(name=llm_extractor.name, params=extraction_params)

    assert llm_extractor.extraction_params.context_attachments == extraction_params["context_attachments"]


def test_llm_extractor__update_context_attachments_from_none_to_value(llm_extractor_no_context_attachments):
    extraction_params = RawLLMExtractionParams(
        custom_instruction=llm_extractor_no_context_attachments.extraction_params.custom_instruction,
        grouping_factor=llm_extractor_no_context_attachments.extraction_params.grouping_factor,
        temperature=llm_extractor_no_context_attachments.extraction_params.temperature,
        top_p=llm_extractor_no_context_attachments.extraction_params.top_p,
        page_span=None,
        context_attachments=random.choice(list(ContextAttachments)),
    )

    llm_extractor_no_context_attachments.update(
        name=llm_extractor_no_context_attachments.name, params=extraction_params
    )

    assert (
        llm_extractor_no_context_attachments.extraction_params.context_attachments
        == extraction_params["context_attachments"]
    )


def test_llm_extractor__add_query__success(
    llm_extractor: LLMExtractor,
    test_code: str,
    test_raw_llm_workflow: RawLLMWorkflow,
    test_raw_data_shape: RawDataShape,
) -> None:
    query = llm_extractor.add_query(
        code=test_code,
        workflow=test_raw_llm_workflow,
        data_shape=test_raw_data_shape,
    )

    assert query
    assert query.code == test_code
    assert query.shape.data_type == test_raw_data_shape["data_type"]
    assert query.shape.cardinality == test_raw_data_shape["cardinality"]
    assert query.shape.include_aliases == test_raw_data_shape["include_aliases"]
    assert query.workflow
    assert query.workflow.entrypoint_node_id == test_raw_llm_workflow["start_node_id"]
    assert query.workflow.output_node_id == test_raw_llm_workflow["end_node_id"]

    for node, raw_node in zip(query.workflow.nodes, test_raw_llm_workflow["nodes"]):
        assert node.id == raw_node["id"]
        assert node.name == raw_node["name"]
        assert node.prompt == raw_node["prompt"]

    for edge, raw_edge in zip(query.workflow.edges, test_raw_llm_workflow["edges"]):
        assert edge.source_id == raw_edge["source_id"]
        assert edge.target_id == raw_edge["target_id"]


def test_llm_extractor__add_query__already_exists(
    llm_extractor: LLMExtractor,
    test_code: str,
    test_raw_llm_workflow: RawLLMWorkflow,
    test_raw_data_shape: RawDataShape,
) -> None:
    llm_extractor.add_query(
        code=test_code,
        workflow=test_raw_llm_workflow,
        data_shape=test_raw_data_shape,
    )

    with pytest.raises(QueryAlreadyExistsError):
        llm_extractor.add_query(
            code=test_code,
            workflow=test_raw_llm_workflow,
            data_shape=test_raw_data_shape,
        )


def test_llm_extractor__update_query__success(
    llm_extractor_with_query: LLMExtractor,
    test_raw_llm_workflow: RawLLMWorkflow,
) -> None:
    updated_prompt = "_CHANGED"
    for node in test_raw_llm_workflow["nodes"]:
        node["prompt"] += updated_prompt

    first_query = llm_extractor_with_query.query_values()[0]
    updated_query = llm_extractor_with_query.update_query(code=first_query.code, workflow=test_raw_llm_workflow)

    assert len([node for node in updated_query.workflow.nodes if updated_prompt in node.prompt]) == len(
        updated_query.workflow.nodes
    )


def test_llm_extractor__update_query__not_found(
    llm_extractor_with_query: LLMExtractor,
    test_raw_llm_workflow: RawLLMWorkflow,
) -> None:
    with pytest.raises(QueryNotFoundError):
        llm_extractor_with_query.update_query(code="fake_code", workflow=test_raw_llm_workflow)


def test_llm_extractor__delete_query__success(
    llm_extractor_with_query: LLMExtractor,
):
    first_query = llm_extractor_with_query.query_values()[0]
    llm_extractor_with_query.delete_query(first_query.code)

    assert first_query.code not in [query.code for query in llm_extractor_with_query.query_values()]


def test_llm_extractor__delete_query__not_found(
    llm_extractor_with_query: LLMExtractor,
):
    with pytest.raises(QueryNotFoundError):
        llm_extractor_with_query.delete_query("fake_code")


def test_llm_extractor__assign_llm(
    llm_extractor_with_query: LLMExtractor,
):
    expected_provider = uuid.uuid4().hex
    expected_model = uuid.uuid4().hex

    llm_extractor_with_query.assign_llm(provider=expected_provider, model=expected_model)

    assert llm_extractor_with_query.llm_reference.provider == expected_provider
    assert llm_extractor_with_query.llm_reference.model == expected_model
