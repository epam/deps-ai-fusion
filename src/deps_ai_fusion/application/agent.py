import logging
from typing import Iterator

from langgraph.errors import GraphRecursionError

from deps_ai_fusion.domain.exceptions.agent import RequiredArgumentMissing

from .i_agent import IAgent
from .i_insights_store import IInsightsStore
from .types import RawAgentArguments, RawAgentResponseChunk, RawContextBundle

__all__ = ["AgentService"]


class AgentService:
    def __init__(self, agent_implementation: IAgent, insights_repository: IInsightsStore) -> None:
        self._agent = agent_implementation
        self._insights_repository = insights_repository

        self._logger = logging.getLogger(__name__)

    def stream_agent_response(
        self,
        *,
        conversation_id: str,
        turn_id: str,
        user_question: str,
        context_bundle: RawContextBundle,
        arguments: RawAgentArguments,
    ) -> Iterator[RawAgentResponseChunk]:
        try:
            for chunk in self._agent.stream(
                conversation_id=conversation_id,
                turn_id=turn_id,
                user_question=user_question,
                arguments=arguments,
                context_bundle=context_bundle,
            ):
                yield chunk
        except RequiredArgumentMissing as exc:
            self._logger.error(f"Agent can't start because of missing required argument: `{exc}`", exc_info=True)
            yield RawAgentResponseChunk(
                type_="Final", text=f"Agent can't start because of missing required argument: `{exc}`"
            )
        except GraphRecursionError as exc:
            self._logger.error(f"Graph recursion error occurred while running the agent: `{exc}`")
            yield RawAgentResponseChunk(
                type_="Final", text=f"Graph recursion error occurred while running the agent: `{exc}`"
            )
        except Exception as exc:
            self._logger.error(f"Unexpected error occurred while running the agent: `{exc}`", exc_info=True)
            yield RawAgentResponseChunk(
                type_="Final", text=f"Unexpected error occurred while running the agent: `{exc}`"
            )

        self._logger.info(f"Agent response stream finished for conversation: `{conversation_id}`")

    def delete_conversation_insights(self, conversation_id: str) -> None:
        self._insights_repository.delete_by_conversation_id(conversation_id=conversation_id)

    def register_agent(self, agent_url: str, agent_timeout: int) -> None:
        self._agent.register(agent_url=agent_url, agent_timeout=agent_timeout)
