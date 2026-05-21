from abc import ABC, abstractmethod

from ....shared import Guard, ImmutableCheck

__all__ = ["Node"]


class Node(ABC):
    id = Guard[str](str, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck())

    def __init__(self, id_: str, name: str) -> None:
        self.id = id_
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.__dict__ == other.__dict__

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
