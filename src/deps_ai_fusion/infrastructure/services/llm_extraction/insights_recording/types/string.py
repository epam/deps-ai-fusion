from deps_extracted_data.model import ExtractedData
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory.response_models import StringResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["StringInsightsRecorder"]


class StringInsightsRecorder(AbstractInsightsRecorder[StringResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[StringResponse],
    ) -> None:
        edata.add_string(
            self.extracted_field_factory.create_string(
                field_code=for_query.code,
                value=StringResponse.parse_llm_response(insight),
                coordinates=None,
                confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
            ),
        )
