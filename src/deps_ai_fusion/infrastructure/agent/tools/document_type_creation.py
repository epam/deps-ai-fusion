from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import ArgsSchema, BaseTool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from deps_ai_fusion.application import LLMExtractionService
from deps_ai_fusion.domain.model import RawLLMExtractionParams, RawLLMExtractor

from ..settings import settings
from ..state import AgentState
from .schemas import DocumentTypeCreationRequest

__all__ = ["DocumentTypeCreationTool"]


class DocumentTypeCreationTool(BaseTool):
    name: str = "create-document-type"
    description: str = (
        "Create a new Document Type for this document. "
        "Only use when no document_type_id exists and after explicit user confirmation. "
        "Reasoning must include the user-confirmed name and why creation is needed now."
    )
    args_schema: ArgsSchema | None = DocumentTypeCreationRequest

    extractors_app: LLMExtractionService

    def _run(
        self,
        document_type_name: str,
        reasoning: str,
        tool_call_id: Annotated[str, InjectedToolCallId()],
        state: Annotated[AgentState, InjectedState()],
    ) -> Command:
        if state.document_type_id is not None:
            raise RuntimeError(
                "This should be unreachable, because DocTypeCreation tool is available only if document_type_id is None."
            )

        dt_id, extractor_id = self.extractors_app.create_extractor(
            document_type_name=document_type_name,
            tenant_id=state.tenant_id,
            extractor=RawLLMExtractor(
                extractor_name=document_type_name,
                provider=settings.default_extractor_provider,
                model=settings.default_extractor_model,
                extraction_params=RawLLMExtractionParams(
                    custom_instruction=settings.default_extractor_custom_instruction,
                    grouping_factor=settings.default_extractor_grouping_factor,
                    temperature=settings.default_extractor_temperature,
                    top_p=settings.default_extractor_top_p,
                    page_span=None,
                    context_attachments=None,
                ),
                extractor_id=None,
            ),
        )

        return Command(
            update={
                "document_type_id": dt_id,
                "extractor_id": extractor_id,
                "messages": [ToolMessage(f"Document type '{document_type_name}' created.", tool_call_id=tool_call_id)],
            },
        )
