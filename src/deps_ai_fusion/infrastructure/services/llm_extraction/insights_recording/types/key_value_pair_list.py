from deps_extracted_data.model import ExtractedData
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory.response_models import KeyValuePairsListResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["KeyValuePairListInsightsRecorder"]


class KeyValuePairListInsightsRecorder(AbstractInsightsRecorder[KeyValuePairsListResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[KeyValuePairsListResponse],
    ) -> None:
        elements = []

        for item in KeyValuePairsListResponse.parse_llm_response(insight):
            key_data = self.field_data_factory.create_string(
                value=item["key"],
                coordinates=None,
                confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
            )
            value_data = self.field_data_factory.create_string(
                value=item["value"],
                coordinates=None,
                confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
            )

            elements.append(self.field_data_factory.create_key_value_pair(key=key_data, value=value_data))

        edata.add_key_value_pair_list(
            self.extracted_field_factory.create_key_value_pair_list(
                field_code=for_query.code,
                elements=elements,
            ),
        )
