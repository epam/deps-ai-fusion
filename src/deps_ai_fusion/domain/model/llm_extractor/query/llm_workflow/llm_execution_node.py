from ....shared import Guard, ImmutableCheck
from .node import Node

__all__ = ["LLMExecutionNode"]


class LLMExecutionNode(Node):
    prompt = Guard[str](str, ImmutableCheck())

    def __init__(self, id_: str, name: str, prompt: str) -> None:
        super().__init__(id_=id_, name=name)
        self.prompt = prompt

    def __repr__(self) -> str:
        return f"LLMExecutionNode(id_={self.id!r}, name={self.name!r}, prompt={self.prompt!r})"

    def __str__(self) -> str:
        return f"LLMExecutionNode: {self.name} (ID: {self.id})"
