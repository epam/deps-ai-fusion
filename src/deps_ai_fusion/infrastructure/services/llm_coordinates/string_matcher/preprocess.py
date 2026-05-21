import re

from ..model.string_matcher.types import NormalizedStr

_STRIP_RE = re.compile(r"[^a-zA-Z0-9\s]")


def normalize(value: str) -> NormalizedStr:
    """
    Strip all non-alphanumeric characters, lowercase, and collapse whitespace.

    Applied identically to both OCR words and LLM-extracted text so that
    punctuation differences and case variations do not prevent matching.

    Example:
        "Oak-Park,"  ->  "oakpark"
        "  Lot  4 " ->  "lot 4"
    """
    return " ".join(_STRIP_RE.sub("", value.lower()).split())


def tokenize(value: str) -> list[NormalizedStr]:
    """
    Normalise value and split it into individual word tokens.

    Used on the LLM-extracted substring before passing it to the DP aligner.

    Example:
        "Lot 4, Block 12"  ->  ["lot", "4", "block", "12"]
    """
    return normalize(value).split()
