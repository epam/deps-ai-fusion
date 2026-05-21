from deps_extracted_data.model import ExtractedData
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory.response_models import KeyValuePairResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["KeyValuePairInsightsRecorder"]


class KeyValuePairInsightsRecorder(AbstractInsightsRecorder[KeyValuePairResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[KeyValuePairResponse],
    ) -> None:
        kv_pair = KeyValuePairResponse.parse_llm_response(insight)

        key_data = self.field_data_factory.create_string(
            value=kv_pair["key"],
            coordinates=None,
            confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
        )
        value_data = self.field_data_factory.create_string(
            value=kv_pair["value"],
            coordinates=None,
            confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
        )

        edata.add_key_value_pair(
            self.extracted_field_factory.create_key_value_pair(
                field_code=for_query.code,
                key=key_data,
                value=value_data,
            ),
        )
