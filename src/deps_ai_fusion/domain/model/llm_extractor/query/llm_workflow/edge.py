from abc import ABC, abstractmethod

from ....shared import Guard, ImmutableCheck

__all__ = ["Edge"]


class Edge(ABC):
    source_id = Guard[str](str, ImmutableCheck())

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Edge) and self.__dict__ == other.__dict__

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
