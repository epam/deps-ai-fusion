import pytest
from deps_gen_ai.providers import ProviderCode

from deps_ai_fusion.domain.model import Cardinality, DataType, LLMExtractorFactory
from deps_ai_fusion.infrastructure.agent import AgentState, GenAIFieldCreationTool
from deps_ai_fusion.infrastructure.agent.tools.schemas import DataShape
from tests.factories import AgentStateFactory
from tests.fakes import FakeLLMExtractorRepository


def test_genai_field_creation_happy_path(
    mock_extraction_proxy,
    fake_llm_extractor_repository: FakeLLMExtractorRepository,
    agent_state_factory: AgentStateFactory,
    genai_field_creation_tool: GenAIFieldCreationTool,
) -> None:
    state: AgentState = agent_state_factory(document_type_id="dt-1")
    mock_extraction_proxy.set_create_field_return_value("field-code")

    fake_llm_extractor_repository.save(
        LLMExtractorFactory.create(
            tenant_id=state.tenant_id,
            document_type_id=state.document_type_id,  # type: ignore
            provider=ProviderCode.EPAM_DIAL,
            name="extractor-name",
            model="extractor-model",
        ),
    )

    cmd = genai_field_creation_tool._run(
        reasoning="r",
        name="FieldName",
        prompts_chain=["p1"],
        response_model=DataShape(
            data_type=DataType.STRING,
            cardinality=Cardinality.SCALAR,
            include_aliases=False,
        ),
        tool_call_id="tc1",
        state=state,
    )

    assert cmd.update["messages"][0].content.startswith("Field 'FieldName' created")
    mock_extraction_proxy.assert_create_field_called()
    mock_extraction_proxy.assert_create_field_called_with(name="FieldName")


def test_genai_field_creation_requires_document_type(
    genai_field_creation_tool: GenAIFieldCreationTool,
    agent_state_factory: AgentStateFactory,
) -> None:
    state: AgentState = agent_state_factory(document_type_id=None)

    with pytest.raises(RuntimeError):
        genai_field_creation_tool._run(
            reasoning="r",
            name="FieldName",
            prompts_chain=["p1"],
            response_model=DataShape(
                data_type=DataType.STRING,
                cardinality=Cardinality.SCALAR,
                include_aliases=False,
            ),
            tool_call_id="tc1",
            state=state,
        )
