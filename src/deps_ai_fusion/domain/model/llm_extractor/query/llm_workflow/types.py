from typing import TypedDict

__all__ = ["RawSequentialEdge", "RawLLMWorkflow", "RawLLMExecutionNode"]


class RawLLMExecutionNode(TypedDict):
    id: str
    name: str
    prompt: str


class RawSequentialEdge(TypedDict):
    source_id: str
    target_id: str


class RawLLMWorkflow(TypedDict):
    start_node_id: str
    end_node_id: str
    nodes: list[RawLLMExecutionNode]
    edges: list[RawSequentialEdge]
