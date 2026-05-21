from abc import ABC, abstractmethod
from typing import Any

from ..model.string_matcher.types import InputWord, Word
from .matcher import StringMatcher
from .utils import bbox_from_flat_polygon

OcrResponse = dict


def _to_flat_polygon(polygon: list) -> list[float]:
    if polygon and isinstance(polygon[0], dict):
        return [coord for p in polygon for coord in (p["x"], p["y"])]
    return polygon if isinstance(polygon, list) else []


class StringMatcherFactory(ABC):
    @abstractmethod
    def create(self, ocr_response: OcrResponse) -> StringMatcher:
        pass


class LayoutStringMatcherFactory:
    """Build a StringMatcher directly from a parsing-service layout dict.

    Supports two word layouts:
    - pages[].words[]                        (flat words per page)
    - pages[].paragraphs[].lines[].words[]   (nested paragraphs/lines)
    """

    def create(self, layout: dict[str, Any]) -> StringMatcher:
        input_words = self._extract_words(layout)
        words = [
            Word(
                page=w["page"],
                content=w["content"],
                polygon=bbox_from_flat_polygon(w["polygon"]),
                confidence=w.get("confidence", 1.0),
            )
            for w in input_words
        ]
        return StringMatcher(words)

    @staticmethod
    def _extract_words(layout: dict[str, Any]) -> list[InputWord]:
        words_out: list[InputWord] = []
        for page_idx, page in enumerate(layout.get("pages") or []):
            flat_words = page.get("words")
            if isinstance(flat_words, list):
                # Format 1: flat words per page
                for w in flat_words:
                    words_out.append(
                        InputWord(
                            page=page_idx,
                            content=w.get("content", ""),
                            polygon=_to_flat_polygon(w.get("polygon") or []),
                            confidence=float(w.get("confidence") or 0.0),
                        )
                    )
            else:
                # Format 2: paragraphs[].lines[].words[]
                for para in page.get("paragraphs") or []:
                    for line in para.get("lines") or []:
                        for w in line.get("words") or []:
                            words_out.append(
                                InputWord(
                                    page=page_idx,
                                    content=w.get("content", ""),
                                    polygon=_to_flat_polygon(w.get("polygon") or []),
                                    confidence=float(w.get("confidence") or 0.0),
                                )
                            )
        return words_out
