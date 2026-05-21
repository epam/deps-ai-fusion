from .model.string_matcher import InputWord, Word
from .model.string_matcher.models import QueryWord
from .model.string_matcher.types import ExtractedValue, FieldCode
from .string_matcher import StringMatcher
from .string_matcher.utils import bbox_from_flat_polygon

__all__ = ["CoordinatesService"]


class CoordinatesService:
    def find_coordinates(
        self, words: list[InputWord], field: dict[FieldCode, ExtractedValue]
    ) -> dict[FieldCode, list[Word]]:
        converted = [self._to_word(w) for w in words]
        matcher = StringMatcher(converted)
        return {
            field_code: self._to_words(matcher.original_words, matcher.find_partial_substring(value))
            for field_code, value in field.items()
        }

    def _to_word(self, w: InputWord) -> Word:
        return Word(
            content=w["content"],
            page=w["page"],
            polygon=bbox_from_flat_polygon(w["polygon"]),
            confidence=w.get("confidence", 1.0),
        )

    def _to_words(self, original_words: list[Word], matched: list[QueryWord]) -> list[Word]:
        result = []
        for qw in matched:
            word = original_words[qw.optimal_index].copy()
            if qw.invalid_left_string or qw.invalid_right_string:
                word["confidence"] = 0.01
            result.append(word)
        return result
