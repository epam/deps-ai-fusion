from deps_extracted_data.model import CheckboxValue, ExtractedData
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory import BooleansListResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["BooleanListInsightsRecorder"]


class BooleanListInsightsRecorder(AbstractInsightsRecorder[BooleansListResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[BooleansListResponse],
    ) -> None:
        elements = [
            self.field_data_factory.create_checkbox(
                value=CheckboxValue.create(element),
                confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
                coordinates=None,
            )
            for element in BooleansListResponse.parse_llm_response(insight)
        ]

        edata.add_checkbox_list(
            self.extracted_field_factory.create_checkbox_list(
                field_code=for_query.code,
                elements=elements,
            ),
        )
