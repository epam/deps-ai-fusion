import logging

from ..model.string_matcher.models import QueryWord
from ..model.string_matcher.types import NormalizedStr, Word
from .core import _build_word_to_positions, construct_optimal_path
from .preprocess import normalize, tokenize

logger = logging.getLogger(__name__)


class StringMatcher:
    """
    Maps LLM-extracted plain text back to the original OCR Word objects.

    Holds two parallel arrays built at construction time:
    - original_words:  the raw Word dicts from Azure OCR, with full spatial metadata.
    - normalized_words: the same words after normalize(), used for comparison.

    The index alignment between the two arrays is the key invariant: position i in
    normalized_words corresponds to position i in original_words.
    """

    def __init__(self, original_words: list[Word]):
        self.original_words, self.normalized_words = self._normalize_words(original_words)
        self._word2positions = _build_word_to_positions(self.normalized_words)

    def find_partial_substring(self, substring: str) -> list[QueryWord]:
        """
        Find the QueryWords that best correspond to the given substring.

        The substring is the plain text returned by the LLM for a field value.
        It is normalised and tokenised, then aligned against the normalised OCR
        words using construct_optimal_path. Each matched QueryWord has optimal_index
        pointing to the corresponding position in original_words.

        Returns an empty list on any error rather than propagating exceptions,
        so a single bad field does not break the whole postprocessing pipeline.

        Args:
            substring: Raw text from the LLM (e.g. "Lot 4 Block 12, Oak Park").

        Returns:
            list[QueryWord]: matched query words in query order, each with optimal_index set.
                             May be shorter than the number of tokens in substring if
                             some tokens had no match in the document.
        """
        try:
            substring_words = tokenize(substring)
            return construct_optimal_path(self.normalized_words, substring_words, word2positions=self._word2positions)
        except Exception as error:
            logger.error("Error in find_partial_substring: %s", error)
            return []

    @staticmethod
    def _normalize_words(words: list[Word]) -> tuple[list[Word], list[NormalizedStr]]:
        """
        Normalise each OCR Word and build two parallel arrays.

        Words whose content reduces to an empty string after normalisation (e.g.
        pure punctuation tokens like "—" or "·") are dropped from both arrays to
        avoid polluting the DP index with unmatchable positions.
        """
        original_words = []
        normalized_words = []

        for word in words:
            content = normalize(word["content"])

            if not content:
                continue

            original_words.append(word)
            normalized_words.append(content)

        return original_words, normalized_words  # noqa
