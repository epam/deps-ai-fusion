from ....shared import Guard, ImmutableCheck
from .edge import Edge

__all__ = ["SequentialEdge"]


class SequentialEdge(Edge):
    target_id = Guard[str](str, ImmutableCheck())

    def __init__(self, source_id: str, target_id: str) -> None:
        super().__init__(source_id)
        self.target_id = target_id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Edge) and self.__dict__ == other.__dict__

    def __repr__(self) -> str:
        return f"SequentialEdge(source_id={self.source_id!r}, target_id={self.target_id!r})"

    def __str__(self) -> str:
        return f"SequentialEdge: SOURCE_ID: {self.source_id} (TARGET_ID: {self.target_id})"
