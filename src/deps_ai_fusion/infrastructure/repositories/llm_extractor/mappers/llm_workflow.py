from typing import Any

from deps_ai_fusion.domain.model import LLMExecutionNode, LLMWorkflow, SequentialEdge

__all__ = ["LLMExecutionNodeMapper"]


class LLMExecutionNodeMapper:
    @staticmethod
    def from_dict(raw_node: dict[str, str]) -> LLMExecutionNode:
        return LLMExecutionNode(
            id_=raw_node["id"],
            name=raw_node["name"],
            prompt=raw_node["prompt"],
        )

    @staticmethod
    def to_dict(node: LLMExecutionNode) -> dict[str, str]:
        return {
            "id": node.id,
            "name": node.name,
            "prompt": node.prompt,
        }


class SequentialEdgeMapper:
    @staticmethod
    def from_dict(raw_edge: dict[str, str]) -> SequentialEdge:
        return SequentialEdge(
            source_id=raw_edge["source_id"],
            target_id=raw_edge["target_id"],
        )

    @staticmethod
    def to_dict(edge: SequentialEdge) -> dict[str, str]:
        return {
            "source_id": edge.source_id,
            "target_id": edge.target_id,
        }


class LLMWorkflowMapper:
    @staticmethod
    def from_dict(raw_llm_worfklow: dict[str, Any]) -> LLMWorkflow:
        return LLMWorkflow(
            entrypoint_node_id=raw_llm_worfklow["entrypoint_node_id"],
            output_node_id=raw_llm_worfklow["output_node_id"],
            nodes=[LLMExecutionNodeMapper.from_dict(node) for node in raw_llm_worfklow["nodes"]],
            edges=[SequentialEdgeMapper.from_dict(edge) for edge in raw_llm_worfklow["edges"]],
        )

    @staticmethod
    def to_dict(llm_workflow: LLMWorkflow) -> dict[str, Any]:
        return {
            "entrypoint_node_id": llm_workflow.entrypoint_node_id,
            "output_node_id": llm_workflow.output_node_id,
            "nodes": [LLMExecutionNodeMapper.to_dict(node) for node in llm_workflow.nodes],
            "edges": [SequentialEdgeMapper.to_dict(edge) for edge in llm_workflow.edges],
        }
