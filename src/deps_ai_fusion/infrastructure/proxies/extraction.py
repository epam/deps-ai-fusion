import logging
from typing import Any, Literal, TypeAlias

from deps_extracted_data.model import ExtractedData
from deps_extracted_data.serializers.v2 import SerializedExtractedData

from .exceptions import ExtractionProxyError
from .proxy import GenericProxy
from .types import AttachmentInfo

__all__ = ["ExtractionProxy"]

FieldCode: TypeAlias = str
ExtractedValue: TypeAlias = str | list[str]
EdataFieldsInfo: TypeAlias = dict[FieldCode, ExtractedValue]


class ExtractionProxy(GenericProxy):
    exception = ExtractionProxyError
    v2_url = "/api/extraction/v2"

    def __init__(self, base_url: str, timeout: int) -> None:
        super().__init__(base_url)
        self._timeout = timeout

        self._logger = logging.getLogger(self.__class__.__name__)

    def attach_extractor(
        self,
        document_type_name: str,
        extractor_type: str,
        extractor_id: str | None,
    ) -> AttachmentInfo:
        data = {
            "name": document_type_name,
            "extractorType": extractor_type,
        }
        if extractor_id:
            data["extractorId"] = extractor_id
        response = self._session.post(
            url=f"{self.base_url}{self.v2_url}/document-types/attach-extractor",
            json=data,
            timeout=self._timeout,
        )

        self._check_response(response)

        response_json = response.json()
        return AttachmentInfo(
            document_type_id=response_json["documentTypeId"],
            extractor_id=response_json["extractorId"],
        )

    def detach_extractor(
        self,
        document_type_id: str,
        extractor_id: str,
    ) -> None:
        url = f"{self.base_url}{self.v2_url}/document-types/{document_type_id}/extractors/{extractor_id}"
        self._check_response(self._session.delete(url, timeout=self._timeout))

    def save_extracted_data(
        self,
        extracted_data: ExtractedData,
    ) -> None:
        self._logger.info("Saving extracted data for document: %s", extracted_data.document_id)

        url = f"{self._base_url}{self.v2_url}/extracted-data/{extracted_data.document_id}"
        json = SerializedExtractedData.from_model(extracted_data).model_dump(by_alias=True, mode="json")

        response = self._session.put(url, json=json, timeout=self._timeout)
        self._check_response(response)

    def create_extraction_field(
        self,
        document_type_id: str,
        extractor_id: str,
        name: str,
        type_: Literal["string", "checkmark", "dict", "list"],
        description: dict[str, Any] | None,
    ) -> FieldCode:
        """This method should be used only by GenAI Fields Agent"""

        self._logger.info(f"Creating extraction field '{name}' for document type '{document_type_id}'")

        data: dict[str, Any] = {
            "name": name,
            "type": type_,
            "extractorId": extractor_id,
            "required": False,
        }

        if description is not None:
            data["description"] = description

        url = f"{self._base_url}{self.v2_url}/document-types/{document_type_id}/extraction-fields"
        response = self._session.post(url, json=data, timeout=self._timeout)

        self._check_response(response)

        return response.json()["pk"]

    def get_extracted_data(self, document_id) -> SerializedExtractedData:
        url = f"{self._base_url}{self.v2_url}/extracted-data/{document_id}"
        response = self._session.get(url, timeout=self._timeout)

        self._check_response(response)

        return SerializedExtractedData.model_validate(response.json())
