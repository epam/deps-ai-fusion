from deps_extracted_data.model import (
    CheckboxValue,
    EntityId,
    ExtractedData,
    GenericData,
)
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory import BooleansListWithAliasesResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["BooleanListWithAliasesInsightsRecorder"]


class BooleanListWithAliasesInsightsRecorder(AbstractInsightsRecorder[BooleansListWithAliasesResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[BooleansListWithAliasesResponse],
    ) -> None:
        elements: list[GenericData] = []
        aliases: dict[EntityId, str] = {}

        for element in BooleansListWithAliasesResponse.parse_llm_response(insight):
            element_data = self.field_data_factory.create_checkbox(
                value=CheckboxValue.create(element["value"]),
                confidence=insight.confidence if insight.confidence is not None else NULL_CONFIDENCE,
                coordinates=None,
            )
            elements.append(element_data)
            alias = element["alias"]
            if alias and alias.strip():
                aliases[element_data.id] = alias

        edata.add_checkbox_list(
            self.extracted_field_factory.create_checkbox_list(
                field_code=for_query.code,
                elements=elements,
                aliases=aliases,
            ),
        )
