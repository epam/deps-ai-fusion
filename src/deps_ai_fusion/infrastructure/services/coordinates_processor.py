import logging
from collections import defaultdict
from typing import Any

from deps_extracted_data.model import ExtractedData
from deps_extracted_data.serializers import SerializedSourceBboxCoordinates
from deps_extracted_data.serializers.base import (
    SerializedBbox,
    SerializedDictFieldData,
    SerializedGenericData,
)
from deps_extracted_data.serializers.v2 import SerializedExtractedData

from ..proxies import ParsingProxy, UnifierProxy
from .llm_coordinates import CoordinatesService
from .llm_coordinates.model.string_matcher import InputWord

__all__ = ["CoordinatesProcessor"]


class CoordinatesProcessor:
    def __init__(self, parsing: ParsingProxy, unifier: UnifierProxy) -> None:
        self._parsing = parsing
        self._unifier = unifier
        self._coordintes_service = CoordinatesService()

        self._logger = logging.getLogger(self.__class__.__name__)

    def add_llm_coordinates(self, document_id: str, extracted_data: SerializedExtractedData) -> ExtractedData | None:
        document_layout = self._parsing.get_document_layout(document_id)
        dl_words = self._extract_all_words(document_layout)

        unified_images = self._unifier.get_original_images(document_id)
        if not unified_images:
            self._logger.info("Can't add coordinates to imageless document.")
            return None
        page_source_id_mapper = {image.page: image.id for image in unified_images}

        for field in extracted_data.fields:
            data = field.data
            if isinstance(data, list):
                for item_data in data:
                    self._process_scalar_field_data(item_data, field.field_code, dl_words, page_source_id_mapper)
            else:
                self._process_scalar_field_data(data, field.field_code, dl_words, page_source_id_mapper)

        return extracted_data.to_model()

    def _extract_all_words(self, document_layout: dict[str, Any]) -> list[InputWord]:
        words: list[InputWord] = []

        for page in document_layout["pages"]:
            page_number = page["pageNumber"]

            for paragraph in page.get("paragraphs", []):
                for line in paragraph.get("lines", []):
                    for raw_word in line.get("words", []):
                        flattened_polygon = [
                            coord
                            for point in raw_word.get("polygon", [])
                            for coord in (point.get("x"), point.get("y"))
                            if coord is not None
                        ]

                        word: InputWord = {
                            "content": str(raw_word.get("content", "")),
                            "page": int(page_number),
                            "polygon": flattened_polygon,
                        }

                        confidence = raw_word.get("confidence")
                        if confidence is not None:
                            word["confidence"] = float(confidence)

                        words.append(word)

        return words

    def _process_scalar_field_data(
        self,
        data: SerializedGenericData | SerializedDictFieldData,
        field_code: str,
        dl_words: list[InputWord],
        page_source_id_mapper: dict[int, str],
    ) -> None:
        if isinstance(data, SerializedDictFieldData):
            self._validate_item_data(data.key)
            self._find_and_add_coordinates(dl_words, page_source_id_mapper, field_code, data.key)

            self._validate_item_data(data.value)
            self._find_and_add_coordinates(dl_words, page_source_id_mapper, field_code, data.value)

        elif isinstance(data, SerializedGenericData):
            self._validate_item_data(data)
            self._find_and_add_coordinates(dl_words, page_source_id_mapper, field_code, data)

    def _validate_item_data(self, data: SerializedGenericData) -> bool:
        return data.value != "" and data.source_bbox_coordinates is not None

    def _find_and_add_coordinates(
        self,
        input_words: list[InputWord],
        page_source_id_mapper: dict[int, str],
        field_code: str,
        data: SerializedGenericData,
    ) -> None:
        response = self._coordintes_service.find_coordinates(
            words=input_words,
            field={field_code: data.value},
        )
        words = response[field_code]
        page_bboxes = defaultdict(list)

        source_bbox_coords = []
        for word in words:
            polygon = word["polygon"]
            bbox = SerializedBbox(x=polygon["x"], y=polygon["y"], w=polygon["w"], h=polygon["h"])
            page_bboxes[word["page"]].append(bbox)

        source_bbox_coords = [
            SerializedSourceBboxCoordinates(
                source_id=page_source_id_mapper[page],
                bboxes=bboxes,
            )
            for page, bboxes in page_bboxes.items()
        ]

        data.source_bbox_coordinates = source_bbox_coords
