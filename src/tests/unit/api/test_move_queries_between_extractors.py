from fastapi import status
from fastapi.testclient import TestClient

from deps_ai_fusion.constants import V1_API_PREFIX
from deps_ai_fusion.domain.events import ExtractionFieldsMoved
from deps_ai_fusion.domain.model import ILLMExtractorRepository, LLMExtractor
from tests.factories import LLMExtractorFactory
from tests.fakes import FakeEventPublisher


def test_move_queries_between_extractors__ok(
    authenticated_client: TestClient,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor_with_query: LLMExtractor,
    fake_event_publisher: FakeEventPublisher,
) -> None:
    source = llm_extractor_with_query
    fake_llm_extractor_repository.save(source)
    target = LLMExtractorFactory.create(
        document_type_id=source.document_type_id(), tenant_id=source.tenant_id(), queries={}
    )
    fake_llm_extractor_repository.save(target)
    code = list(source.queries.keys())[0]

    payload = {
        "sourceExtractorId": source.id(),
        "targetExtractorId": target.id(),
        "fieldsCodes": [code],
    }

    url = f"{V1_API_PREFIX}/document-types/{source.document_type_id()}/llm-extractors/move-queries"
    resp = authenticated_client.post(url, json=payload)
    assert resp.status_code == status.HTTP_200_OK

    new_source = fake_llm_extractor_repository.get(source.id(), source.tenant_id())
    new_target = fake_llm_extractor_repository.get(target.id(), target.tenant_id())
    assert code not in new_source.queries
    assert code in new_target.queries
    assert len(fake_event_publisher.published_events) == 1
    assert fake_event_publisher.published_events == [
        ExtractionFieldsMoved(
            document_type_id=source.document_type_id(),
            source_extractor_id=source.id(),
            target_extractor_id=target.id(),
            fields_codes=[code],
        ),
    ]


def test_move_queries_between_extractors__missing_field__4xx(
    authenticated_client: TestClient,
    fake_llm_extractor_repository: ILLMExtractorRepository,
    llm_extractor_with_query: LLMExtractor,
    fake_event_publisher: FakeEventPublisher,
    test_code: str,
) -> None:
    source = llm_extractor_with_query
    fake_llm_extractor_repository.save(source)

    target = LLMExtractorFactory.create(
        document_type_id=source.document_type_id(), tenant_id=source.tenant_id(), queries={}
    )
    fake_llm_extractor_repository.save(target)

    payload = {
        "sourceExtractorId": source.id(),
        "targetExtractorId": target.id(),
        "fieldsCodes": [test_code, "fake_code"],
    }

    url = f"{V1_API_PREFIX}/document-types/{source.document_type_id()}/llm-extractors/move-queries"
    resp = authenticated_client.post(url, json=payload)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
