import logging
from typing import Any

from .exceptions import ParsingProxyError
from .layout_info import RawLayoutInfo
from .proxy import GenericProxy

__all__ = ["ParsingProxy"]


class ParsingProxy(GenericProxy):
    exception = ParsingProxyError
    v1_url = "/api/parsing/v1"

    def __init__(self, base_url: str, timeout: int) -> None:
        super().__init__(base_url)
        self._timeout = timeout

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_document_layout(self, entity_id: str) -> dict[str, Any]:
        response = self._session.get(
            f"{self._base_url}{self.v1_url}/document-layout/{entity_id}",
            timeout=self._timeout,
            params=self._get_layout_query(entity_id),
        )

        self._check_response(response)

        return response.json()

    def _get_layout_query(self, entity_id: str) -> dict[str, str | list[str]]:
        layout_info = self._get_layout_info(entity_id)

        parsing_type = self._has_text_feature(layout_info["parsingFeatures"])

        return {
            "parsingType": parsing_type or list(layout_info["parsingFeatures"].keys())[0],
            "features": "text",
        }

    def _get_layout_info(self, entity_id: str) -> RawLayoutInfo:
        response = self._session.get(
            f"{self._base_url}{self.v1_url}/document-layout/{entity_id}/info",
            timeout=self._timeout,
        )

        self._check_response(response)

        return response.json()

    def _has_text_feature(self, parsing_features: dict[str, list[str]]) -> str | None:
        return next((key for key, values in parsing_features.items() if "text" in values), None)
