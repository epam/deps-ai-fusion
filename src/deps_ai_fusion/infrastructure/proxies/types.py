from typing import TypedDict

__all__ = ["AttachmentInfo"]


class AttachmentInfo(TypedDict):
    document_type_id: str
    extractor_id: str
