import inspect
import logging

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from deps_ai_fusion.domain.exceptions import AlreadyExistsError, LLMExtractorError
from deps_ai_fusion.domain.model import (
    ILLMExtractorRepository,
    LLMExtractorFactory,
    RawLLMExtractionParams,
)
from deps_ai_fusion.infrastructure.proxies import ExtractionProxy

from .create_llm_extractor_data import CreateLLMExtractorSagaData

__all__ = ["CreateLLMExtractorSteps"]


class CreateLLMExtractorSteps:
    extractor_type = "llm"

    def __init__(
        self,
        extraction_proxy: ExtractionProxy,
        extractor_repository: ILLMExtractorRepository,
    ) -> None:
        self._extraction_proxy = extraction_proxy
        self._extractor_repository = extractor_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    def attach_extractor(self, data: CreateLLMExtractorSagaData) -> None:
        self._logger.debug("Starting <attach_extractor> step with data: %s", data.__dict__)
        try:
            attachment_info = self._extraction_proxy.attach_extractor(
                document_type_name=data.document_type_name,
                extractor_type=self.extractor_type,
                extractor_id=data.extractor_id,
            )
            data.document_type_id = attachment_info["document_type_id"]
            data.extractor_id = attachment_info["extractor_id"]

        except Exception as err:
            self._handle_generic_exception(
                error=err,
                step=inspect.currentframe().f_code.co_name,
                data=data,
            )

    def detach_extractor(self, data: CreateLLMExtractorSagaData) -> None:
        self._logger.debug("Starting <delete_extractor> step with data: %s", data.__dict__)
        try:
            document_type_id = data.document_type_id
            data.document_type_id = None
            self._extraction_proxy.detach_extractor(document_type_id, data.extractor_id)

        except Exception as err:
            if data.original_exc:
                data.original_exc.args = data.original_exc.args + (f"{err.__class__.__name__}: {str(err)}",)
            self._handle_generic_exception(
                error=data.original_exc,
                step=inspect.currentframe().f_code.co_name,
                data=data,
            )

    def create_extractor(self, data: CreateLLMExtractorSagaData) -> None:
        self._logger.debug("Starting <create_extractor> step with data: %s", data.__dict__)
        try:
            extractor = LLMExtractorFactory.create(
                id_=data.extractor_id,
                tenant_id=data.tenant_id,
                document_type_id=data.document_type_id,
                provider=data.provider,
                name=data.extractor_name,
                model=data.model,
                extraction_params=RawLLMExtractionParams(
                    custom_instruction=data.custom_instruction,
                    grouping_factor=data.grouping_factor,
                    temperature=data.temperature,
                    top_p=data.top_p,
                    page_span=data.page_span,
                    context_attachments=data.context_attachments,
                ),
            )
            self._extractor_repository.save(extractor)

        except IntegrityError as err:
            if isinstance(err.orig, UniqueViolation):
                error_message = (
                    f"LLMExtractor with name {data.extractor_name} already exists "
                    + f"for document type with id {data.document_type_id}"
                )
                err = RuntimeError(AlreadyExistsError.code, error_message)

            self._handle_generic_exception(error=err, step=inspect.currentframe().f_code.co_name, data=data)

        except Exception as err:
            self._handle_generic_exception(error=err, step=inspect.currentframe().f_code.co_name, data=data)

    def _handle_generic_exception(self, error: Exception, step: str, data: CreateLLMExtractorSagaData) -> None:
        self._logger.error("Step <%s> fails with error: %s", step, str(error), exc_info=True)
        data.original_exc = LLMExtractorError(*error.args)
        raise RuntimeError(error.args)
