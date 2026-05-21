import logging
import sys
from contextlib import suppress

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    make_message_for_command,
)
from deps_message_flow.commands.consumer import CommandHandlerReplyBuilder
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_message_flow.messaging.common import IMessage

from deps_ai_fusion.application import LLMExtractionService
from deps_ai_fusion.containers import Containers
from deps_ai_fusion.domain.events import (
    ConversationDeleted,
    DocumentTypeDeleted,
    ExtractorDetached,
    ExtractorFieldDeleted,
    PerformExtractionStepReply,
    PerformLLMExtraction,
)
from deps_ai_fusion.domain.exceptions import BusinessError, QueryNotFoundError

from .error_type import ErrorType

__all__ = [
    "extractor_detached_handler",
    "document_type_deleted_handler",
    "perform_extraction_handler",
    "extractor_field_deleted_handler",
    "conversation_deleted_handler",
]

_logger = logging.getLogger(__name__)

REPLY_TO_MOCK = "NONE"


@inject
def perform_extraction_handler(
    command_message: CommandMessage[PerformLLMExtraction],
    current_user_tenant: str = Provide[Containers.current_user_tenant],
    application: LLMExtractionService = Provide[Containers.llm_extraction_service],
) -> list[IMessage]:
    error_type, error_message, traceback = None, None, None

    try:
        application.perform_extraction(
            extractor_id=command_message.command.extractor_id,
            tenant_id=current_user_tenant,
            document_id=command_message.command.document_id,
            llm_type=command_message.command.llm_type,
        )
    except BusinessError as e:
        error_type, error_message, traceback = ErrorType.BUSINESS, str(e), sys.exc_info()
    except Exception as e:
        error_type, error_message, traceback = ErrorType.SYSTEM, str(e), sys.exc_info()

    if error_type is not None:
        _logger.error(
            "Failed to perform extraction for document `%s`! Reason: %s",
            command_message.command.document_id,
            error_message,
            exc_info=traceback,
        )
    command_reply = PerformExtractionStepReply(
        error_type=error_type,
        error_message=error_message,
    )

    message_reply = make_message_for_command(
        channel=command_message.message.get_header(CommandMessageHeaders.REPLY_TO),
        payload=JsonMapper().serialize(command_reply),
        command_type=command_reply.__class__.__name__,
        reply_to=REPLY_TO_MOCK,
    )

    return [CommandHandlerReplyBuilder.with_success(message_reply)]


@inject
def document_type_deleted_handler(
    dee: DomainEventEnvelope[DocumentTypeDeleted],
    application: LLMExtractionService = Provide[Containers.llm_extraction_service],
) -> None:
    application.delete_extractors_for(document_type_id=dee.event.document_type, tenant_id=dee.event.tenant)


@inject
def extractor_detached_handler(
    dee: DomainEventEnvelope[ExtractorDetached],
    tenant_id: str = Provide[Containers.current_user_tenant],
    application: LLMExtractionService = Provide[Containers.llm_extraction_service],
) -> None:
    application.delete_extractor(extractor_id=dee.event.extractor_id, tenant_id=tenant_id)


@inject
def extractor_field_deleted_handler(
    dee: DomainEventEnvelope[ExtractorFieldDeleted],
    tenant_id: str = Provide[Containers.current_user_tenant],
    application: LLMExtractionService = Provide[Containers.llm_extraction_service],
) -> None:
    with suppress(QueryNotFoundError):
        application.delete_query(
            code=dee.event.code,
            extractor_id=dee.event.extractor_id,
            document_type_id=dee.event.document_type_code,
            tenant_id=tenant_id,
        )


@inject
def conversation_deleted_handler(
    dee: DomainEventEnvelope[ConversationDeleted],
    agent_service=Provide[Containers.agent_service],
) -> None:
    conversation_id = dee.event.id
    agent_service.delete_conversation_insights(conversation_id=conversation_id)
    _logger.info("Deleted insights for conversation_id: %s", conversation_id)
