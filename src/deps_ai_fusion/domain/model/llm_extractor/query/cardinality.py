from enum import Enum

__all__ = ["Cardinality"]


class Cardinality(str, Enum):
    SCALAR = "scalar"
    LIST = "list"
