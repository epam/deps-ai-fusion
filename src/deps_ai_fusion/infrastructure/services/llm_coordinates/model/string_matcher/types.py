from typing import NotRequired, TypedDict

OcrWordIndex = int
PathCost = float
PreviousIndex = int
PositionCostEntry = tuple[PathCost, PreviousIndex]
IndexCost = dict[OcrWordIndex, PositionCostEntry]
NormalizedStr = str
WordToPositions = dict[str, list[OcrWordIndex]]
BaseCases = dict[OcrWordIndex, PositionCostEntry]


class Bbox(TypedDict):
    x: float
    y: float
    w: float
    h: float


FieldCode = str
ExtractedValue = str


class InputWord(TypedDict):
    content: str
    page: int
    polygon: list[float]
    confidence: NotRequired[float]


class Word(TypedDict):
    content: str
    page: int
    polygon: Bbox
    confidence: NotRequired[float]
