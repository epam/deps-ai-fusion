from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from deps_extracted_data.model import (
    ExtractedData,
    ExtractedFieldFactory,
    FieldDataFactory,
)
from deps_gen_ai.common import LLMResponse
from pydantic import BaseModel

from deps_ai_fusion.domain.model import Query

__all__ = ["AbstractInsightsRecorder"]

TResponseType = TypeVar("TResponseType", bound=BaseModel)


class AbstractInsightsRecorder(ABC, Generic[TResponseType]):
    extracted_field_factory = ExtractedFieldFactory()
    field_data_factory = FieldDataFactory()

    @abstractmethod
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[TResponseType],
    ) -> None:
        ...
