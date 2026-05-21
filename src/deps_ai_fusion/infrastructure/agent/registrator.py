import logging
from typing import Any

from deps_ai_fusion.application.i_agent import IAgent
from deps_ai_fusion.infrastructure.proxies import AgenticAIProxy, MetaAgentProxy

__all__ = ["AgentRegistrator"]


class AgentRegistrator:
    def __init__(self, agentic_ai_proxy: AgenticAIProxy, meta_agent_proxy: MetaAgentProxy) -> None:
        self._agentic_ai_proxy = agentic_ai_proxy
        self._meta_agent_proxy = meta_agent_proxy

        self._logger = logging.getLogger(self.__class__.__name__)

    def register(
        self,
        agent: IAgent,
        agent_url: str,
        timeout: int,
    ) -> None:
        self._register_agent_manifest(
            code=agent.code, name=agent.name, description=agent.description, agent_url=agent_url, timeout=timeout
        )
        self._register_tool_set(code=agent.code, name=agent.name, tools=agent.available_tools)

    def _register_tool_set(self, code: str, name: str, tools: list[dict[str, Any]]) -> None:
        self._agentic_ai_proxy.register_tool_set(
            code=code,
            name=name,
            tools=tools,
        )

    def _register_agent_manifest(self, code: str, name: str, description: str, agent_url: str, timeout: int) -> None:
        self._meta_agent_proxy.register_agent_manifest(
            code=code,
            name=name,
            description=description,
            agent_url=agent_url,
            timeout=timeout,
        )
