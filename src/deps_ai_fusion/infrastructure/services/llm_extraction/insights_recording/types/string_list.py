from deps_extracted_data.model import ExtractedData
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory import StringsListResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["StringListInsightsRecorder"]


class StringListInsightsRecorder(AbstractInsightsRecorder[StringsListResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[StringsListResponse],
    ) -> None:
        elements = [
            self.field_data_factory.create_string(
                value=element,
                confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
                coordinates=None,
            )
            for element in StringsListResponse.parse_llm_response(insight)
        ]

        edata.add_string_list(
            self.extracted_field_factory.create_string_list(
                field_code=for_query.code,
                elements=elements,
            ),
        )
