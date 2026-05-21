import logging

from .exceptions import UnifierProxyError
from .original_image import OriginalImage
from .proxy import GenericProxy

__all__ = ["UnifierProxy"]


class UnifierProxy(GenericProxy):
    exception = UnifierProxyError
    v1_url = "/api/unifier/v1/unified_data"

    def __init__(self, base_url: str, timeout: int) -> None:
        super().__init__(base_url)
        self._timeout = timeout

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_original_images(self, document_id: str) -> list[OriginalImage]:
        self._logger.info(f"Getting unified images for document {document_id}")

        response = self._session.get(
            url=f"{self.base_url}{self.v1_url}/{document_id}",
            params={"unified_data_types": "image"},
            timeout=self._timeout,
        )

        self._check_response(response)

        return [
            OriginalImage(id=image["id"], page=image["page"], path=image["blobName"])
            for image in response.json()["elements"]
            if image["originalImageId"] is None
        ]
