from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

__all__ = ["PerformLLMExtraction", "PerformExtractionStepReply"]


@dataclass
class PerformLLMExtraction(Command):
    extractor_id: str
    document_id: str

    llm_type: Optional[str] = None


@dataclass
class PerformExtractionStepReply(Command):
    error_type: str | None
    error_message: str | None
