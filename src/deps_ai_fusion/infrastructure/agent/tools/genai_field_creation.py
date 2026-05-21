from typing import Annotated, Any, Literal
from uuid import uuid4

from langchain_core.messages import ToolMessage
from langchain_core.tools import ArgsSchema, BaseTool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from deps_ai_fusion.application import LLMExtractionService
from deps_ai_fusion.domain.model import (
    Cardinality,
    DataType,
    RawDataShape,
    RawLLMWorkflow,
)
from deps_ai_fusion.infrastructure.proxies import ExtractionProxy

from ..state import AgentState
from .schemas import CreateGenAIFieldRequest, DataShape

__all__ = ["GenAIFieldCreationTool"]


class GenAIFieldCreationTool(BaseTool):
    name: str = "create-genai-field"
    description: str = (
        "Create a new GenAI Field on the existing Document Type and register its prompts_chain. "
        "Use only after user explicitly approves the field name, prompts and response_model, and ideally after validation via perform-llm-extraction. "
        "Prefer the smallest viable prompts_chain (often one prompt); add steps only when strictly necessary. "
        "Reasoning should summarize the user approval and why creation is safe now."
    )
    args_schema: ArgsSchema | None = CreateGenAIFieldRequest

    extractors_app: LLMExtractionService
    extraction_proxy: ExtractionProxy

    def _run(
        self,
        reasoning: str,
        name: str,
        prompts_chain: list[str],
        response_model: DataShape,
        tool_call_id: Annotated[str, InjectedToolCallId()],
        state: Annotated[AgentState, InjectedState()],
    ) -> Command:
        if state.document_type_id is None:
            raise RuntimeError("Document type ID is required to create a GenAI field.")

        tenant_id = state.tenant_id
        document_type_id = state.document_type_id

        extractor_id = self._resolve_extractor_id(state=state, document_type_id=document_type_id, tenant_id=tenant_id)

        field_code = self._create_extraction_field(
            document_type_id=document_type_id,
            extractor_id=extractor_id,
            name=name,
            shape=response_model,
        )

        self._create_genai_query(
            document_type_id=document_type_id,
            tenant_id=tenant_id,
            extractor_id=extractor_id,
            field_code=field_code,
            prompts_chain=prompts_chain,
            response_model=response_model,
        )

        return Command(
            update={
                "extractor_id": extractor_id,
                "messages": [
                    ToolMessage(
                        f"Field '{name}' created and query registered under extractor '{extractor_id}'.",
                        tool_call_id=tool_call_id,
                    ),
                ],
            },
        )

    def _resolve_extractor_id(self, state: AgentState, document_type_id: str, tenant_id: str) -> str:
        if (extractor_id := state.extractor_id) is not None:
            return extractor_id

        extractors = self.extractors_app.get_llm_extractors_for_document_type(
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

        if not extractors:
            raise RuntimeError(
                "This Document Type can't be used to create GenAI Fields. User has to create at least one LLM Extractor for it first.",
            )

        return extractors[0].id()

    def _create_extraction_field(
        self,
        document_type_id: str,
        extractor_id: str,
        name: str,
        shape: DataShape,
    ) -> str:
        dtype_field_type_mapping: dict[DataType, Literal["string", "checkmark", "dict", "list"]] = {
            DataType.STRING: "string",
            DataType.BOOLEAN: "checkmark",
            DataType.KEY_VALUE_PAIR: "dict",
        }
        dtype_description_mapping: dict[DataType, None | dict[str, Any]] = {
            DataType.STRING: None,
            DataType.BOOLEAN: None,
            DataType.KEY_VALUE_PAIR: {
                "keyType": "string",
                "valueType": "string",
            },
        }

        field_type = dtype_field_type_mapping[shape.data_type] if shape.cardinality == Cardinality.SCALAR else "list"
        description = (
            dtype_description_mapping[shape.data_type]
            if shape.cardinality == Cardinality.SCALAR
            else {
                "baseType": dtype_field_type_mapping[shape.data_type],
                "baseTypeMeta": dtype_description_mapping[shape.data_type] or {},
            }
        )

        return self.extraction_proxy.create_extraction_field(
            document_type_id=document_type_id,
            extractor_id=extractor_id,
            name=name,
            type_=field_type,
            description=description,
        )

    def _create_genai_query(
        self,
        document_type_id: str,
        tenant_id: str,
        extractor_id: str,
        field_code: str,
        prompts_chain: list[str],
        response_model: DataShape,
    ) -> None:
        node_ids = [uuid4().hex for _ in range(len(prompts_chain))]
        raw_workflow = RawLLMWorkflow(
            start_node_id=node_ids[0],
            end_node_id=node_ids[-1],
            nodes=[
                {"id": node_ids[idx], "name": f"Step {idx + 1}", "prompt": prompt}
                for idx, prompt in enumerate(prompts_chain)
            ],
            edges=[{"source_id": node_ids[idx], "target_id": node_ids[idx + 1]} for idx in range(len(node_ids) - 1)],
        )

        raw_data_shape = RawDataShape(
            data_type=response_model.data_type,
            cardinality=response_model.cardinality,
            include_aliases=response_model.include_aliases,
        )

        self.extractors_app.add_query(
            code=field_code,
            raw_workflow=raw_workflow,
            raw_data_shape=raw_data_shape,
            document_type_id=document_type_id,
            extractor_id=extractor_id,
            tenant_id=tenant_id,
        )
