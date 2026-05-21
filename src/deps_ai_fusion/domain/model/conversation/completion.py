import uuid
from datetime import datetime, timezone

from ..shared import Guard, ImmutableCheck, LLMReference
from .raw_history import RawCompletion

__all__ = ["Completion"]


class Completion:
    code = Guard[str](str, ImmutableCheck())
    question = Guard[str](str, ImmutableCheck())
    response = Guard[str](str, ImmutableCheck())
    llm_reference = Guard[LLMReference](LLMReference, ImmutableCheck())
    confidence = Guard[float](float, ImmutableCheck())
    created_at = Guard[datetime](datetime, ImmutableCheck())

    def __init__(
        self,
        question: str,
        response: str,
        provider: str,
        model: str,
        code: str | None = None,
        created_at: datetime | None = None,
        confidence: float | None = None,
    ) -> None:
        self.question = question
        self.response = response
        self.llm_reference = LLMReference(provider=provider, model=model)

        if confidence is not None:
            self.confidence = confidence

        self.code = code or uuid.uuid4().hex
        self.created_at = created_at or datetime.now(tz=timezone.utc)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Completion)
            and self.code == other.code
            and self.llm_reference == other.llm_reference
            and self.question == other.question
            and self.response == other.response
            and self.created_at == other.created_at
        )

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.code = },",
                f"{self.llm_reference = },",
                f"{self.question = }>",
                f"{self.response = }>",
                f"{self.confidence = }>",
                f"{self.created_at = }>",
            ),
        )

    def dump(self) -> RawCompletion:
        return {
            "question": self.question,
            "response": self.response,
        }
