from typing import TypedDict

from .cardinality import Cardinality
from .data_type import DataType

__all__ = ["RawDataShape"]


class RawDataShape(TypedDict):
    data_type: DataType
    cardinality: Cardinality
    include_aliases: bool
