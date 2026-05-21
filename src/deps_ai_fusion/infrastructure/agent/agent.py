import logging
from functools import cached_property
from typing import Any, Iterator

from langgraph.graph.state import RunnableConfig

from deps_ai_fusion.application.i_agent import IAgent
from deps_ai_fusion.application.types import (
    RawAgentArguments,
    RawAgentResponseChunk,
    RawContextBundle,
)

from .agentic_workflow_factory import AgenticWorkflowFactory
from .registrator import AgentRegistrator
from .response import AgentChunk
from .settings import settings
from .state import AgentState

__all__ = ["GenAIQueriesAgent"]


class GenAIQueriesAgent(IAgent):
    name: str = "GenAI Queries Agent"
    code: str = "genai-queries-agent"
    description: str = settings.agent_description

    _max_steps_for_single_request: int = 15

    def __init__(
        self,
        workflow_factory: AgenticWorkflowFactory,
        agent_registrator: AgentRegistrator,
    ) -> None:
        self._workflow_factory = workflow_factory
        self._agent_registrator = agent_registrator

        self._logger = logging.getLogger(__name__)

    @cached_property
    def available_tools(self) -> list[dict[str, Any]]:
        return self._workflow_factory.available_tools()

    def register(self, agent_url: str, agent_timeout: int) -> None:
        self._agent_registrator.register(
            agent=self,
            agent_url=agent_url,
            timeout=agent_timeout,
        )

    def stream(
        self,
        *,
        conversation_id: str,
        turn_id: str,
        user_question: str,
        arguments: RawAgentArguments,
        context_bundle: RawContextBundle,
    ) -> Iterator[RawAgentResponseChunk]:
        state = self._initialize_agent_state(
            conversation_id=conversation_id,
            arguments=arguments,
            context_bundle=context_bundle,
            question=user_question,
        )

        agent = self._workflow_factory.create_workflow()
        config = RunnableConfig(recursion_limit=self._max_steps_for_single_request)

        last_emitted: RawAgentResponseChunk | None = None
        for _, chunk in agent.stream(state, stream_mode="values", config=config, subgraphs=True):
            if not AgentChunk.supports(chunk):  # type: ignore
                continue

            current = AgentChunk.from_langchain_message(chunk["messages"][-1]).to_raw()  # type: ignore

            if current == last_emitted:
                continue

            last_emitted = current
            yield current

    def _initialize_agent_state(
        self,
        conversation_id: str,
        arguments: RawAgentArguments,
        context_bundle: RawContextBundle,
        question: str,
    ) -> AgentState:
        state = AgentState.from_arguments(
            conversation_id=conversation_id,
            args=arguments,
            context=context_bundle,
            question=question,
        )

        self._logger.info(f"Initialized agent for new user question on document: `{state.document_id}`")

        return state
