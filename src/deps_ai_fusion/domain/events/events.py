from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = [
    "LLMRequestLogged",
    "DocumentTypeDeleted",
    "ExtractorDetached",
    "ExtractorFieldDeleted",
    "ExtractionFieldsMoved",
    "ConversationDeleted",
]


@dataclass
class LLMRequestLogged(DomainEvent):
    entity_id: str
    user_id: str
    tenant_id: str
    provider: str
    model: str
    confidence: float | None = None


@dataclass
class DocumentTypeDeleted(DomainEvent):
    document_type: str
    tenant: str


@dataclass
class ExtractorDetached(DomainEvent):
    document_type_id: str
    extractor_id: str
    extractor_type: str


@dataclass
class ExtractorFieldDeleted(DomainEvent):
    code: str
    document_type_code: str
    extractor_type: str
    extractor_id: str


@dataclass
class ExtractionFieldsMoved(DomainEvent):
    document_type_id: str
    source_extractor_id: str
    target_extractor_id: str
    fields_codes: list[str]


@dataclass
class ConversationDeleted(DomainEvent):
    id: str
