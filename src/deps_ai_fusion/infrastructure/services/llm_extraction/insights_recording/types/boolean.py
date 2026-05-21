from deps_extracted_data.model import CheckboxValue, ExtractedData
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory.response_models import BooleanResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["BooleanInsightsRecorder"]


class BooleanInsightsRecorder(AbstractInsightsRecorder[BooleanResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[BooleanResponse],
    ) -> None:
        edata.add_checkbox(
            self.extracted_field_factory.create_checkbox(
                field_code=for_query.code,
                value=CheckboxValue.create(BooleanResponse.parse_llm_response(insight)),
                coordinates=None,
                confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
            ),
        )
