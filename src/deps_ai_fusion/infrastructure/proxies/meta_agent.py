import logging

from .proxy import GenericProxy

__all__ = ["MetaAgentProxy"]


class MetaAgentProxy(GenericProxy):
    url = "/api/meta-agent/v1/manifests"

    def __init__(self, base_url: str, timeout: int) -> None:
        super().__init__(base_url)
        self._timeout = timeout

        self._logger = logging.getLogger(self.__class__.__name__)

    def register_agent_manifest(self, code: str, name: str, description: str, agent_url: str, timeout: int) -> None:
        url = f"{self.base_url}{self.url}"
        payload = {
            "code": code,
            "name": name,
            "description": description,
            "url": agent_url,
            "timeout": timeout,
        }

        self._check_response(self._session.post(url, json=payload, timeout=self._timeout))
