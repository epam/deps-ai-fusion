import logging
from urllib.parse import urljoin

from .exceptions import FileStorageProxyError
from .proxy import GenericProxy

__all__ = ["FileStorageProxy"]


class FileStorageProxy(GenericProxy):
    exception = FileStorageProxyError
    url_prefix = "/api/storage/v1/file/"

    def __init__(self, base_url: str, timeout: int) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._download_url = urljoin(self.base_url, self.url_prefix)

        self._logger = logging.getLogger(self.__class__.__name__)

    def download_content(self, filepath: str) -> bytes:
        response = self._session.get(url=urljoin(self._download_url, filepath), timeout=self._timeout)

        self._check_response(response)

        return response.content
