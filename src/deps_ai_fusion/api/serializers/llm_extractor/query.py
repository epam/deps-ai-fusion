from pydantic import Field

from deps_ai_fusion.domain.model import Cardinality, DataType, Query, RawDataShape

from ..base import ConfiguredBaseModel
from .workflow import SerializedLLMWorkflow

__all__ = ["SerializedQuery"]


class SerializedDataShape(ConfiguredBaseModel):
    data_type: DataType = Field(default=DataType.STRING, alias="dataType")
    cardinality: Cardinality
    include_aliases: bool = Field(..., alias="includeAliases")

    def to_dict(self) -> RawDataShape:
        return RawDataShape(
            data_type=self.data_type,
            cardinality=self.cardinality,
            include_aliases=self.include_aliases,
        )


class SerializedQuery(ConfiguredBaseModel):
    code: str
    workflow: SerializedLLMWorkflow
    shape: SerializedDataShape

    @classmethod
    def from_model(cls, query: Query) -> "SerializedQuery":
        return cls(
            code=query.code,
            workflow=SerializedLLMWorkflow.from_model(query.workflow),
            shape=SerializedDataShape(
                data_type=query.shape.data_type,
                cardinality=query.shape.cardinality,
                include_aliases=query.shape.include_aliases,
            ),
        )
