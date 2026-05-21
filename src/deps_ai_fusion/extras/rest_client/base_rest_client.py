import logging
from abc import abstractmethod

import requests

from .adapter import DEPSHTTPSAdapter

__all__ = ["AbstractRESTClient"]


class AbstractRESTClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        access_token: str | None = None,
    ) -> None:
        self._base_url = base_url

        self._api_key = api_key
        self._access_token = access_token

        self._logger = logging.getLogger(self.__class__.__name__)

        self._session = requests.Session()
        self._initialize()

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def base_url(self) -> str:
        return self._base_url

    def _initialize(self) -> None:
        self._mount_adapter()
        self._set_session_headers()
        self._set_authentication()

    def _mount_adapter(self) -> None:
        self._session.mount(self._base_url, DEPSHTTPSAdapter())

    def _set_session_headers(self) -> None:
        pass

    @abstractmethod
    def _set_authentication(self) -> None:
        ...
