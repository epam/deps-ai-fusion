from typing import Any

from deps_ai_fusion.domain.model import Cardinality, DataShape, DataType, Query

from .llm_workflow import LLMWorkflowMapper

__all__ = ["QueryMapper"]


class DataShapeMapper:
    @staticmethod
    def from_dict(raw_data_shape: dict[str, str | bool]) -> DataShape:
        return DataShape(
            data_type=DataType(raw_data_shape["data_type"]),
            cardinality=Cardinality(raw_data_shape["cardinality"]),
            include_aliases=raw_data_shape["include_aliases"],
        )

    @staticmethod
    def to_dict(data_shape: DataShape) -> dict[str, str | bool]:
        return {
            "data_type": data_shape.data_type,
            "cardinality": data_shape.cardinality,
            "include_aliases": data_shape.include_aliases,
        }


class QueryMapper:
    @staticmethod
    def from_dict(raw_query: dict[str, Any]) -> Query:
        return Query(
            code=raw_query["code"],
            workflow=LLMWorkflowMapper.from_dict(raw_query["workflow"]),
            shape=DataShapeMapper.from_dict(raw_query["shape"]),
        )

    @staticmethod
    def to_dict(query: Query) -> dict[str, Any]:
        return {
            "code": query.code,
            "workflow": LLMWorkflowMapper.to_dict(query.workflow),
            "shape": DataShapeMapper.to_dict(query.shape),
        }
