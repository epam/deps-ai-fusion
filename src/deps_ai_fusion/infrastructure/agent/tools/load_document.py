from typing import Annotated

from deps_gen_ai.common import ContextReference
from deps_gen_ai.context_creators import PlainLayoutContextCreator
from langchain_core.tools import BaseTool
from langgraph.prebuilt import InjectedState

from ..state import AgentState

__all__ = ["DocumentLoadingTool"]


class DocumentLoadingTool(BaseTool):
    name: str = "load-document-layout"
    description: str = (
        "Load the full document text context into memory for grounding. "
        "Use before answering questions that depend on document content or before testing prompts. "
        "Keep reasoning short (<=20 words) explaining why loading is necessary now."
    )

    layout_cc: PlainLayoutContextCreator

    def _run(
        self,
        reasoning: str,
        state: Annotated[AgentState, InjectedState()],
    ) -> str:
        return self.layout_cc.context_of(
            ContextReference.from_raw_params(entity_id=state.document_id),
        )
