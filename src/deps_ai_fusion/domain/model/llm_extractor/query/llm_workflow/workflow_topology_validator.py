import logging
import uuid
from typing import TYPE_CHECKING, cast

from .....exceptions import InvariantViolationError
from .llm_execution_node import LLMExecutionNode
from .sequential_edge import SequentialEdge

if TYPE_CHECKING:
    from .llm_workflow import LLMWorkflow

__all__ = ["WorkflowTopologyValidator"]


REQUIRED_UUID_VERSION = 4


class WorkflowTopologyValidator:
    def __init__(self, workflow: "LLMWorkflow") -> None:
        self._workflow = workflow

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def nodes(self) -> list[LLMExecutionNode]:
        return cast(list[LLMExecutionNode], self._workflow.nodes)

    @property
    def edges(self) -> list[SequentialEdge]:
        return cast(list[SequentialEdge], self._workflow.edges)

    def validate(self) -> None:
        self._validate_node_ids()
        self._validate_entrypoint_and_output()
        self._validate_graph_structure()

    def _validate_node_ids(self) -> None:
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise InvariantViolationError("LLMWorkflow has duplicate node IDs found in the graph.")

        for id_ in node_ids:
            try:
                if uuid.UUID(id_).version != REQUIRED_UUID_VERSION:
                    raise ValueError  # noqa: WPS220

            except ValueError:
                self._logger.error("LLMWorkflow invalid UUID4 string for node ID: %s", id_)
                raise InvariantViolationError("LLMWorkflow invalid UUID4 string for node ID.")

    def _validate_entrypoint_and_output(self) -> None:
        node_ids = {node.id for node in self.nodes}

        if self._workflow.entrypoint_node_id not in node_ids:
            raise InvariantViolationError(
                f"LLMWorkflow entrypoint node ID '{self._workflow.entrypoint_node_id}' not found in nodes.",
            )

        if self._workflow.output_node_id not in node_ids:
            raise InvariantViolationError(
                f"LLMWorkflow output node ID '{self._workflow.output_node_id}' not found in nodes.",
            )

    def _validate_graph_structure(self) -> None:
        if len(self.edges) != len(self.nodes) - 1:
            raise InvariantViolationError("LLMWorkflow graph structure is invalid: edges must connect all nodes.")

        if not self.edges:
            if self._workflow.entrypoint_node_id != self._workflow.output_node_id:
                raise InvariantViolationError(
                    "LLMWorkflow graph structure is invalid: single node must have entrypoint equal to output.",
                )

        self._check_graph_connectivity_and_cycles()

    def _check_graph_connectivity_and_cycles(self) -> None:
        visited_nodes = set()
        current_node_id = self._workflow.entrypoint_node_id

        for _ in self.edges:
            edge = self._find_edge_by_source(current_node_id)

            if edge.target_id in visited_nodes:
                self._logger.error("LLMWorkflow graph contains a cycle.")
                raise InvariantViolationError("LLMWorkflow graph must be acyclic.")

            visited_nodes.add(current_node_id)
            current_node_id = edge.target_id

        visited_nodes.add(current_node_id)

        if len(visited_nodes) != len(self.nodes):
            raise InvariantViolationError("LLMWorkflow graph is not connected: not all nodes are reachable.")

        if current_node_id != self._workflow.output_node_id:
            raise InvariantViolationError("LLMWorkflow graph structure is invalid: output node not reached.")

    def _find_edge_by_source(self, source_id: str) -> SequentialEdge:
        try:
            return next(edge for edge in self.edges if edge.source_id == source_id)

        except StopIteration:
            self._logger.error("LLMWorkflow no edge found for source ID: %s", source_id)
            raise InvariantViolationError("LLMWorkflow graph structure is invalid: missing edge.")
