from deps_extracted_data.model import EntityId, ExtractedData
from deps_extracted_data.model.extracted_data.default_confidence import NULL_CONFIDENCE
from deps_gen_ai.common import LLMResponse

from deps_ai_fusion.domain.model import Query

from ...genai_query_factory import KeyValuePairsListWithAliasesResponse
from .abstract import AbstractInsightsRecorder

__all__ = ["KeyValuePairListWithAliasesInsightsRecorder"]


class KeyValuePairListWithAliasesInsightsRecorder(AbstractInsightsRecorder[KeyValuePairsListWithAliasesResponse]):
    def record_insights(
        self,
        edata: ExtractedData,
        for_query: Query,
        insight: LLMResponse[KeyValuePairsListWithAliasesResponse],
    ) -> None:
        elements = []
        aliases: dict[EntityId, str] = {}

        for item in KeyValuePairsListWithAliasesResponse.parse_llm_response(insight):
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

            kvp = self.field_data_factory.create_key_value_pair(key=key_data, value=value_data)
            elements.append(kvp)
            alias = item["alias"]
            if alias and alias.strip():
                aliases[kvp.id] = alias

        edata.add_key_value_pair_list(
            self.extracted_field_factory.create_key_value_pair_list(
                field_code=for_query.code,
                elements=elements,
                aliases=aliases,
            ),
        )
