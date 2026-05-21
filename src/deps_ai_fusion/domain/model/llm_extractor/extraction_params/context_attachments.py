from enum import Enum

__all__ = ["ContextAttachments"]


class ContextAttachments(str, Enum):
    DOCUMENT_IMAGES = "document_images"
    ORIGINAL_DOCUMENT = "original_document"
