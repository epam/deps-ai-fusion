from typing import Iterator

from deps_ai_fusion.application.types import (
    RawAgentArguments,
    RawAgentResponseChunk,
    RawContextBundle,
)
from deps_ai_fusion.infrastructure.agent import AgentChunk, GenAIQueriesAgent

__all__ = ["FakeAgent"]


class FakeAgent(GenAIQueriesAgent):
    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        self._chunks: list[AgentChunk] = []
        self._exception: Exception | None = None

    def set_chunks(self, chunks: list[AgentChunk]) -> None:
        self._exception = None
        self._chunks = chunks

    def set_exception(self, exc: Exception) -> None:
        self._chunks = []
        self._exception = exc

    def stream(
        self,
        *,
        conversation_id: str,
        turn_id: str,
        user_question: str,
        arguments: RawAgentArguments,
        context_bundle: RawContextBundle,
    ) -> Iterator[RawAgentResponseChunk]:
        if self._exception is not None:
            raise self._exception

        for ch in self._chunks:
            yield ch.to_raw()
