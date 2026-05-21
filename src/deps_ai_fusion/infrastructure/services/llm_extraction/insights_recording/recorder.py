from typing import TypeAlias

from deps_extracted_data.model import ExtractedData
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Cardinality, DataType, Query

from .types import (
    AbstractInsightsRecorder,
    BooleanInsightsRecorder,
    BooleanListInsightsRecorder,
    BooleanListWithAliasesInsightsRecorder,
    KeyValuePairInsightsRecorder,
    KeyValuePairListInsightsRecorder,
    KeyValuePairListWithAliasesInsightsRecorder,
    StringInsightsRecorder,
    StringListInsightsRecorder,
    StringListWithAliasesInsightsRecorder,
)

__all__ = ["InsightsRecorder"]

IncludeAliases: TypeAlias = bool


class InsightsRecorder:
    def __init__(self) -> None:
        self._recorders: dict[tuple[DataType, Cardinality, IncludeAliases], AbstractInsightsRecorder] = {
            (DataType.STRING, Cardinality.SCALAR, False): StringInsightsRecorder(),
            (DataType.BOOLEAN, Cardinality.SCALAR, False): BooleanInsightsRecorder(),
            (DataType.KEY_VALUE_PAIR, Cardinality.SCALAR, False): KeyValuePairInsightsRecorder(),
            (DataType.STRING, Cardinality.LIST, False): StringListInsightsRecorder(),
            (DataType.BOOLEAN, Cardinality.LIST, False): BooleanListInsightsRecorder(),
            (DataType.KEY_VALUE_PAIR, Cardinality.LIST, False): KeyValuePairListInsightsRecorder(),
            (DataType.STRING, Cardinality.LIST, True): StringListWithAliasesInsightsRecorder(),
            (DataType.BOOLEAN, Cardinality.LIST, True): BooleanListWithAliasesInsightsRecorder(),
            (DataType.KEY_VALUE_PAIR, Cardinality.LIST, True): KeyValuePairListWithAliasesInsightsRecorder(),
        }

    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse,
    ) -> None:
        recorder = self._recorders[
            (for_query.shape.data_type, for_query.shape.cardinality, for_query.shape.include_aliases)
        ]

        recorder.record_insights(edata, for_query, insight)
