from ...shared import Guard, ImmutableCheck
from .code import Code
from .data_shape import DataShape
from .llm_workflow import LLMExecutionNode, LLMWorkflow, RawLLMWorkflow, SequentialEdge

__all__ = ["Query"]


class Query:
    code = Guard[Code](Code, ImmutableCheck())
    workflow = Guard[LLMWorkflow](LLMWorkflow)
    shape = Guard[DataShape](DataShape, ImmutableCheck())

    def __init__(self, code: Code, workflow: LLMWorkflow, shape: DataShape) -> None:
        self.code = code
        self.workflow = workflow
        self.shape = shape

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Query) and other.code == self.code

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.code = },",
                f"{self.workflow = },",
                f"{self.shape = }>",
            ),
        )

    def update(self, workflow: RawLLMWorkflow) -> None:
        self.workflow = self.workflow.create_updated(
            entrypoint_node_id=workflow["start_node_id"],
            output_node_id=workflow["end_node_id"],
            nodes=[
                LLMExecutionNode(id_=node["id"], name=node["name"], prompt=node["prompt"]) for node in workflow["nodes"]
            ],
            edges=[
                SequentialEdge(source_id=edge["source_id"], target_id=edge["target_id"]) for edge in workflow["edges"]
            ],
        )
