import logging

from ....shared import Guard, ImmutableCheck, LengthCheck
from .edge import Edge
from .node import Node
from .workflow_topology_validator import WorkflowTopologyValidator

__all__ = ["LLMWorkflow"]


class LLMWorkflow:
    entrypoint_node_id = Guard[str](str, ImmutableCheck())
    output_node_id = Guard[str](str, ImmutableCheck())
    nodes = Guard[list[Node]](list, ImmutableCheck(), LengthCheck(min_length=1))
    edges = Guard[list[Edge]](list, ImmutableCheck())

    def __init__(self, entrypoint_node_id: str, output_node_id: str, nodes: list[Node], edges: list[Edge]) -> None:
        self.entrypoint_node_id = entrypoint_node_id
        self.output_node_id = output_node_id
        self.nodes = nodes
        self.edges = edges

        self._logger = logging.getLogger(self.__class__.__name__)

        self.validator.validate()

    @property
    def validator(self) -> WorkflowTopologyValidator:
        return WorkflowTopologyValidator(self)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, LLMWorkflow)
            and other.entrypoint_node_id == self.entrypoint_node_id
            and other.output_node_id == self.output_node_id
            and other.nodes == self.nodes
            and other.edges == self.edges
        )

    def __repr__(self) -> str:
        return (
            f"LLMWorkflow(entrypoint_node_id={self.entrypoint_node_id!r}, "
            f"output_node_id={self.output_node_id!r}, "
            f"nodes={self.nodes!r}, edges={self.edges!r})"
        )

    def __str__(self) -> str:
        return (
            f"LLMWorkflow with entrypoint_node_id='{self.entrypoint_node_id}', "
            f"output_node_id='{self.output_node_id}', "
            f"{len(self.nodes)} nodes, and {len(self.edges)} edges."
        )

    def create_updated(
        self,
        entrypoint_node_id: str,
        output_node_id: str,
        nodes: list[Node],
        edges: list[Edge],
    ) -> "LLMWorkflow":
        return LLMWorkflow(
            entrypoint_node_id=entrypoint_node_id,
            output_node_id=output_node_id,
            nodes=nodes,
            edges=edges,
        )
