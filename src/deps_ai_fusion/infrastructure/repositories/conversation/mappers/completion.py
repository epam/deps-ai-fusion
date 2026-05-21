from datetime import datetime, timezone
from typing import Any

from deps_ai_fusion.domain.model.conversation import Completion

__all__ = ["CompletionMapper"]


class CompletionMapper:
    @staticmethod
    def from_dict(raw_completion: dict[str, Any]) -> Completion:
        return Completion(
            code=raw_completion["code"],
            provider=raw_completion["provider"],
            model=raw_completion["model"],
            question=raw_completion["question"],
            response=raw_completion["response"],
            confidence=raw_completion.get("confidence"),
            created_at=datetime.fromtimestamp(raw_completion["created_at"], tz=timezone.utc),
        )

    @staticmethod
    def to_dict(completion: Completion) -> dict[str, Any]:
        return {
            "code": completion.code,
            "provider": completion.llm_reference.provider,
            "model": completion.llm_reference.model,
            "question": completion.question,
            "response": completion.response,
            "confidence": completion.confidence,
            "created_at": completion.created_at.timestamp(),
        }
