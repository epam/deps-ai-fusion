import logging
from typing import TypeAlias

from .proxy import GenericProxy

__all__ = ["AgenticAIProxy"]

ToolData: TypeAlias = dict[str, dict[str, str]]


class AgenticAIProxy(GenericProxy):
    internal_url = "/api/agentic-ai/internal"

    def __init__(self, base_url: str, timeout: int) -> None:
        super().__init__(base_url)
        self._timeout = timeout

        self._logger = logging.getLogger(self.__class__.__name__)

    def register_tool_set(self, code: str, name: str, tools: list[ToolData]) -> None:
        url = f"{self.base_url}{self.internal_url}/tool-sets"
        payload = {
            "code": code,
            "name": name,
            "tools": tools,
        }

        self._check_response(self._session.put(url, json=payload, timeout=self._timeout))
