import uuid

import pytest
from deps_gen_ai.providers import ProviderCode
from sqlalchemy.exc import IntegrityError

from deps_ai_fusion.domain.model import ILLMExtractorRepository
from deps_ai_fusion.domain.model.llm_extractor import LLMExtractor
from deps_ai_fusion.domain.model.llm_extractor import (
    LLMExtractorFactory as NativeLLMExtractorFactory,
)
from deps_ai_fusion.domain.model.llm_extractor import (
    LLMExtractorsFilter,
    RawLLMExtractionParams,
)
from deps_ai_fusion.infrastructure.repositories import LLMExtractorRepository
from tests.factories import LLMExtractorFactory


def _sorting_by_id(extractor: LLMExtractor):
    return extractor.id()


def test_save_and_get(
    llm_extractor_repository: LLMExtractorRepository,
    llm_extractor_with_query: LLMExtractor,
) -> None:
    llm_extractor_repository.save(llm_extractor_with_query)

    saved = llm_extractor_repository.get(
        id_=llm_extractor_with_query.id(),
        tenant_id=llm_extractor_with_query.tenant_id(),
    )

    assert saved == llm_extractor_with_query


def test_get__does_not_exist__none(llm_extractor_repository: LLMExtractorRepository) -> None:
    assert llm_extractor_repository.get(id_="fake_id", tenant_id="fake_tenant") is None


def test_find_for_document_type(
    llm_extractor_repository: LLMExtractorRepository,
    llm_extractor: LLMExtractor,
) -> None:
    llm_extractor_repository.save(llm_extractor)

    saved = llm_extractor_repository.find_for_document_type(
        id_=llm_extractor.id(),
        document_type_id=llm_extractor.document_type_id(),
        tenant_id=llm_extractor.tenant_id(),
    )

    assert saved == llm_extractor


def test_find_for_document_type__does_not_exist__none(
    llm_extractor_repository: LLMExtractorRepository,
    llm_extractor: LLMExtractor,
) -> None:
    llm_extractor_repository.save(llm_extractor)

    assert (
        llm_extractor_repository.find_for_document_type(
            id_=llm_extractor.id(),
            document_type_id="fake_doctype_id",
            tenant_id=llm_extractor.tenant_id(),
        )
        is None
    )


def test_save_updated__updated(
    llm_extractor_repository: LLMExtractorRepository,
    llm_extractor: LLMExtractor,
) -> None:
    llm_extractor_repository.save(llm_extractor)

    extraction_params = RawLLMExtractionParams(
        custom_instruction=uuid.uuid4().hex,
        grouping_factor=None,
        temperature=None,
        top_p=None,
        page_span=None,
        context_attachments=None,
    )

    llm_extractor.update(
        params=extraction_params,
        name=(name := uuid.uuid4().hex),
    )

    llm_extractor_repository.save(llm_extractor)

    saved_updated_llm_extractor = llm_extractor_repository.get(
        id_=llm_extractor.id(),
        tenant_id=llm_extractor.tenant_id(),
    )

    assert saved_updated_llm_extractor.name == name
    assert saved_updated_llm_extractor.extraction_params.custom_instruction == extraction_params["custom_instruction"]
    assert saved_updated_llm_extractor.extraction_params.grouping_factor is not None
    assert saved_updated_llm_extractor.extraction_params.temperature is not None
    assert saved_updated_llm_extractor.extraction_params.top_p is not None


def save_unique_constraint_violated__error(
    llm_extractor_repository: LLMExtractorRepository,
    llm_extractor: LLMExtractor,
) -> None:
    llm_extractor_repository.save(llm_extractor)

    new_llm_extractor = LLMExtractorFactory.create(
        name=llm_extractor.name,
        document_type_id=llm_extractor.document_type_id(),
        tenant_id=llm_extractor.tenant_id(),
    )

    with pytest.raises(IntegrityError):
        llm_extractor_repository.save(new_llm_extractor)


def test_find_by_name_for_document_type(
    llm_extractor_repository: LLMExtractorRepository,
    llm_extractor: LLMExtractor,
) -> None:
    llm_extractor_repository.save(llm_extractor)

    assert (
        llm_extractor_repository.find_by_name_for_document_type(
            name=llm_extractor.name,
            document_type_id=llm_extractor.document_type_id(),
            tenant_id=llm_extractor.tenant_id(),
        )
        is not None
    )


def test_find_by_name_for_document_type__does_not_exist__none(llm_extractor_repository: LLMExtractorRepository) -> None:
    assert (
        llm_extractor_repository.find_by_name_for_document_type(
            name="name",
            document_type_id="document_type_id",
            tenant_id="tenant_id",
        )
        is None
    )


def test_delete_extractor__deleted(
    llm_extractor_repository: LLMExtractorRepository,
    document_type_id: str,
    tenant_id: str,
) -> None:
    saved_extractor_ids = []
    for _ in range(3):
        extractor = NativeLLMExtractorFactory.create(
            tenant_id=tenant_id,
            document_type_id=document_type_id,
            provider=ProviderCode.EPAM_DIAL,
            name=uuid.uuid4().hex,
            model=uuid.uuid4().hex,
        )
        saved_extractor_ids.append(extractor.id())
        llm_extractor_repository.save(extractor)

    id_for_delete = saved_extractor_ids[-1]
    llm_extractor_repository.delete(extractor_id=id_for_delete, tenant_id=tenant_id)

    assert llm_extractor_repository.get(id_for_delete, tenant_id) is None


def test_delete_for_document_type__deleted(
    llm_extractor_repository: LLMExtractorRepository,
    document_type_id: str,
    tenant_id: str,
) -> None:
    saved_extractor_ids = []
    for _ in range(3):
        extractor = NativeLLMExtractorFactory.create(
            tenant_id=tenant_id,
            document_type_id=document_type_id,
            provider=ProviderCode.EPAM_DIAL,
            name=uuid.uuid4().hex,
            model=uuid.uuid4().hex,
        )
        saved_extractor_ids.append(extractor.id())
        llm_extractor_repository.save(extractor)

    llm_extractor_repository.delete_for_document_type(document_type_id=document_type_id, tenant_id=tenant_id)

    for id_ in saved_extractor_ids:
        assert llm_extractor_repository.get(id_, tenant_id) is None


def test_find_by_id__ok(test_saved_llm_extractor, llm_extractor_repository):
    extractor = llm_extractor_repository.find_by_id(test_saved_llm_extractor.id(), test_saved_llm_extractor.tenant_id())

    assert extractor == test_saved_llm_extractor


def test_find_by_id__extractor_doesnt_exsit__no_error(test_saved_llm_extractor, llm_extractor_repository):
    extractor = llm_extractor_repository.find_by_id("fake_id", test_saved_llm_extractor.tenant_id())

    assert not extractor


def test_find_by_filter__id(
    llm_extractor_repository: ILLMExtractorRepository,
):
    expected_ids = [uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex]
    expected_extractors = []

    for id_ in expected_ids:
        llm_extractor = NativeLLMExtractorFactory.create(
            id_=id_,
            tenant_id=uuid.uuid4().hex,
            document_type_id=uuid.uuid4().hex,
            provider=ProviderCode.EPAM_DIAL,
            name=uuid.uuid4().hex,
            model=uuid.uuid4().hex,
        )
        expected_extractors.append(llm_extractor)
        llm_extractor_repository.save(llm_extractor)

    for _ in range(3):
        llm_extractor_repository.save(
            NativeLLMExtractorFactory.create(
                id_=uuid.uuid4().hex,
                tenant_id=uuid.uuid4().hex,
                document_type_id=uuid.uuid4().hex,
                provider=ProviderCode.EPAM_DIAL,
                name=uuid.uuid4().hex,
                model=uuid.uuid4().hex,
            )
        )

    filter_ = LLMExtractorsFilter(ids=expected_ids)
    llm_extractors = llm_extractor_repository.find_by_filter(filter_)

    assert sorted(expected_extractors, key=_sorting_by_id) == sorted(llm_extractors, key=_sorting_by_id)


def test_find_by_filter__tenant_id(
    llm_extractor_repository: ILLMExtractorRepository,
):
    expected_tenant_id = uuid.uuid4().hex
    expected_extractors = []

    for _ in range(3):
        llm_extractor = NativeLLMExtractorFactory.create(
            tenant_id=expected_tenant_id,
            document_type_id=uuid.uuid4().hex,
            provider=ProviderCode.EPAM_DIAL,
            name=uuid.uuid4().hex,
            model=uuid.uuid4().hex,
        )
        expected_extractors.append(llm_extractor)
        llm_extractor_repository.save(llm_extractor)

    for _ in range(3):
        llm_extractor_repository.save(
            NativeLLMExtractorFactory.create(
                tenant_id=uuid.uuid4().hex,
                document_type_id=uuid.uuid4().hex,
                provider=ProviderCode.EPAM_DIAL,
                name=uuid.uuid4().hex,
                model=uuid.uuid4().hex,
            )
        )

    filter_ = LLMExtractorsFilter(tenant_id=expected_tenant_id)

    llm_extractors = llm_extractor_repository.find_by_filter(filter_)

    assert sorted(expected_extractors, key=_sorting_by_id) == sorted(llm_extractors, key=_sorting_by_id)


def test_find_by_filter__document_type_id(
    llm_extractor_repository: ILLMExtractorRepository,
):
    expected_doctype_id = uuid.uuid4().hex
    expected_extractors = []

    for _ in range(3):
        llm_extractor = NativeLLMExtractorFactory.create(
            tenant_id=uuid.uuid4().hex,
            document_type_id=expected_doctype_id,
            provider=ProviderCode.EPAM_DIAL,
            name=uuid.uuid4().hex,
            model=uuid.uuid4().hex,
        )
        expected_extractors.append(llm_extractor)
        llm_extractor_repository.save(llm_extractor)

    for _ in range(3):
        llm_extractor_repository.save(
            NativeLLMExtractorFactory.create(
                tenant_id=uuid.uuid4().hex,
                document_type_id=uuid.uuid4().hex,
                provider=ProviderCode.EPAM_DIAL,
                name=uuid.uuid4().hex,
                model=uuid.uuid4().hex,
            ),
        )

    filter_ = LLMExtractorsFilter(document_type_id=expected_doctype_id)

    llm_extractors = llm_extractor_repository.find_by_filter(filter_)

    assert sorted(expected_extractors, key=_sorting_by_id) == sorted(llm_extractors, key=_sorting_by_id)
