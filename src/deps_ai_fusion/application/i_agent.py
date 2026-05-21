from typing import Any, Iterator, Protocol

from .types import RawAgentArguments, RawAgentResponseChunk, RawContextBundle

__all__ = ["IAgent"]


class IAgent(Protocol):
    name: str
    code: str
    description: str

    @property
    def available_tools(self) -> list[dict[str, Any]]:
        ...

    def register(self, agent_url: str, agent_timeout: int) -> None:
        ...

    def stream(
        self,
        *,
        conversation_id: str,
        turn_id: str,
        user_question: str,
        arguments: RawAgentArguments,
        context_bundle: RawContextBundle,
    ) -> Iterator[RawAgentResponseChunk]:
        ...
