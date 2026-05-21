from deps_message_flow.events.common import DomainEvent

from ...events import LLMRequestLogged
from ...exceptions import CompletionLimitExceededError
from ..shared import EntityId, Guard, ImmutableCheck, TenantId, UserId
from .completion import Completion
from .raw_history import RawConversationHistory

__all__ = ["Conversation"]


class Conversation:
    _MAX_COMPLETIONS = 100
    _HISTORY_LIMIT = 20

    entity_id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    user_id = Guard[UserId](UserId, ImmutableCheck())
    completions = Guard[dict[str, Completion]](dict)

    def __init__(
        self,
        entity_id: str,
        tenant_id: str,
        user_id: str,
        completions: list[Completion],
        events: list[DomainEvent] | None = None,
    ) -> None:
        self.entity_id = EntityId(entity_id)
        self.tenant_id = TenantId(tenant_id)
        self.user_id = UserId(user_id)
        self.completions = {completion.code: completion for completion in completions}

        self._events: list[DomainEvent] = events or []

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Conversation)
            and self.entity_id == other.entity_id
            and self.tenant_id == other.tenant_id
            and self.user_id == other.user_id
        )

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.entity_id = },",
                f"{self.tenant_id = },",
                f"{self.user_id = }>",
                f"{self.completions = }>",
            ),
        )

    @property
    def events(self) -> list[DomainEvent]:
        return self._events

    def drain_events(self) -> list[DomainEvent]:
        events = self._events
        self._events = []

        return events

    def add_completion(
        self,
        provider: str,
        model: str,
        question: str,
        response: str,
        confidence: float | None,
    ) -> Completion:
        self._check_completion_limit()

        completion = Completion(
            question=question,
            response=response,
            provider=provider,
            model=model,
            confidence=confidence,
        )

        self.completions[completion.code] = completion
        self._track_completion_creation(completion)

        return completion

    def clear(self) -> None:
        self.completions = {}

    def remove_completions(self, codes: list[str]) -> None:
        for code in codes:
            if code in self.completions.keys():
                del self.completions[code]

    def form_history(self) -> RawConversationHistory:
        return {
            "completions": [completion.dump() for completion in self._visible_history()],
        }

    def _track_completion_creation(
        self,
        completion: Completion,
    ) -> None:
        self._events.append(
            LLMRequestLogged(
                entity_id=self.entity_id(),
                tenant_id=self.tenant_id(),
                user_id=self.user_id(),
                model=completion.llm_reference.model,
                provider=completion.llm_reference.provider,
                confidence=completion.confidence,
            ),
        )

    def _check_completion_limit(self) -> None:
        if len(self.completions) >= self._MAX_COMPLETIONS:
            raise CompletionLimitExceededError(self.entity_id(), self._MAX_COMPLETIONS)

    def _visible_history(self) -> list[Completion]:
        return list(self.completions.values())[-self._HISTORY_LIMIT :]
