import logging

from deps_gen_ai.exceptions import ModelNotFound
from deps_gen_ai.providers import ProviderCode
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_ai_fusion.domain.exceptions import (
    LLMExtractorError,
    LLMExtractorNotFoundError,
)
from deps_ai_fusion.domain.model import (
    ContextAttachments,
    ILLMExtractorRepository,
    LLMExtractor,
    LLMExtractorsFilter,
    Query,
    RawDataShape,
    RawLLMExtractionParams,
    RawLLMExtractor,
    RawLLMWorkflow,
    RawPageSpan,
)
from deps_ai_fusion.messaging.sagas import (
    CreateLLMExtractorSaga,
    CreateLLMExtractorSagaData,
)

from ..constants import EXTRACTION_FIELDS_DESTINATION
from .i_control_llms import IControlLLMs
from .types import DocumentTypeId, ExtractorId

__all__ = ["LLMExtractionService"]


class LLMExtractionService:
    _DEFAULT_PROVIDER = ProviderCode.EPAM_DIAL.value

    def __init__(
        self,
        llm_extractor_repository: ILLMExtractorRepository,
        sagas: list[Saga],
        saga_instance_factory: SagaInstanceFactory,
        llms_controller: IControlLLMs,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._llm_extractor_repository = llm_extractor_repository
        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory
        self._llms_controller = llms_controller
        self._domain_event_publisher = domain_event_publisher

        self._logger = logging.getLogger(self.__class__.__name__)

    def add_query(
        self,
        code: str,
        raw_workflow: RawLLMWorkflow,
        raw_data_shape: RawDataShape,
        document_type_id: str,
        extractor_id: str,
        tenant_id: str,
    ) -> Query:
        llm_extractor = self._find_llm_extractor_for_document_type(
            extractor_id=extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

        query_object = llm_extractor.add_query(code=code, workflow=raw_workflow, data_shape=raw_data_shape)
        self._llm_extractor_repository.save(llm_extractor)

        return query_object

    def update_query(
        self,
        code: str,
        raw_workflow: RawLLMWorkflow,
        extractor_id: str,
        document_type_id: str,
        tenant_id: str,
    ) -> Query:
        llm_extractor = self._find_llm_extractor_for_document_type(
            extractor_id=extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )
        query_object = llm_extractor.update_query(code=code, workflow=raw_workflow)
        self._llm_extractor_repository.save(llm_extractor)

        return query_object

    def delete_query(
        self,
        code: str,
        extractor_id: str,
        document_type_id: str,
        tenant_id: str,
    ) -> None:
        self._logger.info(
            f"Deleting query `{code}` for extractor `{extractor_id}` and document type `{document_type_id}`",
        )

        llm_extractor = self._find_llm_extractor_for_document_type(
            extractor_id=extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

        llm_extractor.delete_query(code=code)
        self._llm_extractor_repository.save(llm_extractor)

    def create_extractor(
        self,
        extractor: RawLLMExtractor,
        document_type_name: str,
        tenant_id: str,
    ) -> tuple[DocumentTypeId, ExtractorId]:
        self._check_llm_exists(provider=extractor["provider"], model=extractor["model"])

        self._logger.info(
            "Starting CreateLLMExtractorSaga with name: %s, tenant_id: %s, model: %s, provider: %s",
            extractor["extractor_name"],
            tenant_id,
            extractor["model"],
            extractor["provider"],
        )
        try:
            extraction_params = extractor["extraction_params"]
            saga_data = CreateLLMExtractorSagaData(
                extractor_name=extractor["extractor_name"],
                document_type_name=document_type_name,
                tenant_id=tenant_id,
                model=extractor["model"],
                provider=extractor["provider"],
                custom_instruction=extraction_params["custom_instruction"],
                grouping_factor=extraction_params["grouping_factor"],
                temperature=extraction_params["temperature"],
                top_p=extraction_params["top_p"],
                page_span=extraction_params["page_span"],
                context_attachments=extraction_params["context_attachments"],
                extractor_id=extractor["extractor_id"],
            )

            self._saga_instance_factory.create(
                saga=self._sagas[CreateLLMExtractorSaga],
                data=saga_data,
            )

        except Exception as err:
            raise LLMExtractorError(*err.args)

        if exc := saga_data.original_exc:
            raise exc

        return saga_data.document_type_id, saga_data.extractor_id

    def update_extractor(
        self,
        extractor_id: str,
        document_type_id: str,
        tenant_id: str,
        name: str,
        custom_instruction: str,
        grouping_factor: int,
        temperature: float,
        top_p: float,
        page_span: RawPageSpan | None = None,
        context_attachments: ContextAttachments | None = None,
    ) -> None:
        llm_extractor = self._find_llm_extractor_for_document_type(
            extractor_id=extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

        llm_extractor.update(
            name=name,
            params=RawLLMExtractionParams(
                custom_instruction=custom_instruction,
                grouping_factor=grouping_factor,
                temperature=temperature,
                top_p=top_p,
                page_span=page_span,
                context_attachments=context_attachments,
            ),
        )
        self._llm_extractor_repository.save(llm_extractor)

    def assign_llm_to_extractor(
        self,
        document_type_id: str,
        extractor_id: str,
        tenant_id: str,
        provider: ProviderCode,
        model: str,
    ) -> None:
        llm_extractor = self._find_llm_extractor_for_document_type(
            extractor_id=extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

        self._check_llm_exists(provider=provider.value, model=model)
        llm_extractor.assign_llm(provider=provider.value, model=model)

        self._llm_extractor_repository.save(llm_extractor)

    def delete_extractor(self, extractor_id: str, tenant_id: str) -> None:
        self._llm_extractor_repository.delete(extractor_id=extractor_id, tenant_id=tenant_id)

    def delete_extractors_for(self, document_type_id: str, tenant_id: str) -> None:
        self._llm_extractor_repository.delete_for_document_type(document_type_id=document_type_id, tenant_id=tenant_id)

    def perform_extraction(
        self,
        extractor_id: str,
        tenant_id: str,
        document_id: str,
        llm_type: str | None = None,
    ) -> None:
        if (extractor := self._find_extractor_by(extractor_id, tenant_id)) and extractor.queries:
            self._llms_controller.execute_extractor(
                llm_extractor=extractor,
                document_id=document_id,
                override_llm=llm_type,
            )

    def get_llm_extractors_for_document_type(
        self,
        document_type_id: str,
        tenant_id: str,
    ) -> list[LLMExtractor]:
        filter_ = LLMExtractorsFilter(
            tenant_id=tenant_id,
            document_type_id=document_type_id,
        )

        llm_extractors = self._llm_extractor_repository.find_by_filter(filter_)

        return llm_extractors

    def move_queries_between_extractors(
        self,
        document_type_id: str,
        source_extractor_id: str,
        target_extractor_id: str,
        tenant_id: str,
        fields_codes: list,
    ):
        source_llm_extractor = self._find_llm_extractor_for_document_type(
            extractor_id=source_extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )
        target_llm_extractor = self._find_llm_extractor_for_document_type(
            extractor_id=target_extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

        target_llm_extractor.move_query_from(source_llm_extractor, fields_codes)

        self._llm_extractor_repository.save_all([source_llm_extractor, target_llm_extractor])

        self._publish_events(target_llm_extractor)

    def _find_extractor_by(self, extractor_id: str, tenant_id: str) -> LLMExtractor:
        if extractor := self._llm_extractor_repository.find_by_id(extractor_id=extractor_id, tenant_id=tenant_id):
            return extractor

        raise LLMExtractorNotFoundError(id_=extractor_id, tenant_id=tenant_id)

    def _find_llm_extractor_for_document_type(
        self,
        extractor_id: str,
        document_type_id: str,
        tenant_id: str,
    ) -> LLMExtractor:
        llm_extractor = self._llm_extractor_repository.find_for_document_type(
            id_=extractor_id,
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )
        if llm_extractor is None:
            raise LLMExtractorNotFoundError(id_=extractor_id, tenant_id=tenant_id)

        return llm_extractor

    def _check_llm_exists(self, provider: str, model: str) -> None:
        if not self._llms_controller.llm_exists(provider=provider, model=model):
            raise ModelNotFound(model=model)

    def _publish_events(self, extractor: LLMExtractor) -> None:
        if extractor.events:
            self._domain_event_publisher.publish(
                aggregate_type=EXTRACTION_FIELDS_DESTINATION,
                aggregate_id=extractor.id(),
                domain_events=extractor.drain_events(),
            )
