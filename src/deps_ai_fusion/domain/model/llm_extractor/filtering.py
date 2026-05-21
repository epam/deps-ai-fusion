from dataclasses import dataclass
from typing import Optional

__all__ = ["LLMExtractorsFilter"]


@dataclass
class LLMExtractorsFilter:
    ids: Optional[list[str]] = None
    tenant_id: Optional[str] = None
    document_type_id: Optional[str] = None
