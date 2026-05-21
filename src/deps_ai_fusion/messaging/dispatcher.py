import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_ai_fusion.constants import (
    COMMANDS_CHANNEL,
    COMMANDS_QUEUE,
    CONVERSATION_DESTINATION,
    DOCUMENT_TYPE_EXCHANGER,
    EVENTS_QUEUE,
    EXTRACTION_EXCHANGE,
)
from deps_ai_fusion.domain.events import (
    ConversationDeleted,
    DocumentTypeDeleted,
    ExtractorDetached,
    ExtractorFieldDeleted,
    PerformLLMExtraction,
)

_logger = logging.getLogger(__name__)


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_ai_fusion.messaging.handlers import (  # noqa: WPS433
        conversation_deleted_handler,
        document_type_deleted_handler,
        extractor_detached_handler,
        extractor_field_deleted_handler,
        perform_extraction_handler,
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(DOCUMENT_TYPE_EXCHANGER)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .and_for_aggregate_type(EXTRACTION_EXCHANGE)
        .on_event(ExtractorDetached, extractor_detached_handler)
        .on_event(ExtractorFieldDeleted, extractor_field_deleted_handler)
        .and_for_aggregate_type(CONVERSATION_DESTINATION)
        .on_event(ConversationDeleted, conversation_deleted_handler)
        .for_queue(EVENTS_QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_CHANNEL)
        .on_message(PerformLLMExtraction, perform_extraction_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming....")

    return subscriber
