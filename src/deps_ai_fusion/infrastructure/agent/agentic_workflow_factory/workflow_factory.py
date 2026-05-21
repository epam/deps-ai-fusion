from typing import Any, Literal

from langchain_core.messages import SystemMessage
from langgraph.graph.state import END, CompiledStateGraph, StateGraph
from langgraph.prebuilt import create_react_agent

from deps_ai_fusion.application import IInsightsStore
from deps_ai_fusion.infrastructure.agent.persistance.models import InsightsPayload

from ..settings import AgentSettings
from ..state import AgentState
from ..tools import (
    DocumentLoadingTool,
    DocumentTypeCreationTool,
    GenAIFieldCreationTool,
    PerformLLMExtractionTool,
)
from .provider_factory import ModelProviderFactory
from .system_message import (
    SYSTEM_MESSAGE_EXISTING_DOCUMENT_TYPE,
    SYSTEM_MESSAGE_UNKNOWN_DOCUMENT_TYPE,
)

__all__ = ["AgenticWorkflowFactory"]


class AgenticWorkflowFactory:
    def __init__(
        self,
        document_loader: DocumentLoadingTool,
        document_type_creation: DocumentTypeCreationTool,
        genai_field_creation: GenAIFieldCreationTool,
        perform_llm_extraction: PerformLLMExtractionTool,
        insights_store: IInsightsStore,
    ) -> None:
        self._settings = AgentSettings()  # type: ignore[call-arg]

        self._document_loader = document_loader
        self._document_type_creation = document_type_creation
        self._genai_field_creation = genai_field_creation
        self._perform_llm_extraction = perform_llm_extraction
        self._insights_store = insights_store

        self.llm = ModelProviderFactory.from_settings(self._settings).create_llm()

    def create_workflow(self) -> CompiledStateGraph:
        main_agent = self._existing_document_type_workflow()
        bootstrap_agent = self._bootstrap_document_type_workflow()

        graph_builder = StateGraph(AgentState)

        graph_builder.add_node("main_agent", main_agent)
        graph_builder.add_node("bootstrap_agent", bootstrap_agent)
        graph_builder.add_node("load_insights", self._load_insights)
        graph_builder.add_node("assemble_context", self._assemble_context)
        graph_builder.add_node("persist_insights", self._persist_insights)

        graph_builder.set_entry_point("load_insights")
        graph_builder.add_edge("load_insights", "assemble_context")

        # First agent is chosen based on existence of document_type_id
        graph_builder.add_conditional_edges("assemble_context", self._route_to_first_agent)
        graph_builder.add_conditional_edges("bootstrap_agent", self._after_bootstrap_agent)

        graph_builder.add_edge("main_agent", "persist_insights")
        graph_builder.add_edge("persist_insights", END)

        return graph_builder.compile()

    def available_tools(self) -> list[dict[str, Any]]:
        def create_tool_info(tool_name: str, parameters: list[dict[str, Any]]) -> dict[str, Any]:  # noqa: WPS430
            return {
                "code": tool_name,
                "name": " ".join(tool_name.split("-")).title(),
                "parameters": parameters,
            }

        tools: list[dict[str, Any]] = []

        tools.append(
            create_tool_info(
                tool_name=self._document_loader.name,
                parameters=[{"name": "document_id"}],
            )
        )

        tools.append(
            create_tool_info(
                tool_name=self._perform_llm_extraction.name,
                parameters=[{"name": "document_id"}],
            )
        )
        tools.append(
            create_tool_info(
                tool_name=self._document_type_creation.name,
                parameters=[{"name": "document_id"}],
            )
        )

        tools.append(
            create_tool_info(
                tool_name=self._genai_field_creation.name,
                parameters=[{"name": "document_id"}, {"name": "document_type_id"}],
            )
        )

        return tools

    def _existing_document_type_workflow(self) -> CompiledStateGraph:
        return create_react_agent(
            model=self.llm,
            prompt=SYSTEM_MESSAGE_EXISTING_DOCUMENT_TYPE,
            tools=[self._document_loader, self._genai_field_creation, self._perform_llm_extraction],
            state_schema=AgentState,
        )

    def _bootstrap_document_type_workflow(self) -> CompiledStateGraph:
        return create_react_agent(
            model=self.llm,
            prompt=SYSTEM_MESSAGE_UNKNOWN_DOCUMENT_TYPE,
            tools=[self._document_loader, self._perform_llm_extraction, self._document_type_creation],
            state_schema=AgentState,
        )

    @staticmethod
    def _after_bootstrap_agent(state: AgentState) -> Literal["main_agent", "persist_insights"]:
        if state.document_type_id is not None:
            return "main_agent"

        return "persist_insights"

    @staticmethod
    def _route_to_first_agent(state: AgentState) -> Literal["main_agent", "bootstrap_agent"]:
        return "main_agent" if state.document_type_id is not None else "bootstrap_agent"

    def _load_insights(self, state: AgentState) -> AgentState:
        if (loaded := self._insights_store.load(state.conversation_id, state.tenant_id)) is None:
            return state

        state.insights = loaded
        return state

    def _assemble_context(self, state: AgentState) -> AgentState:
        if not state.insights:
            return state

        insights_text = "\n".join(f"- {item}" for item in state.insights)
        insights_msg = SystemMessage(
            content=f"Persistent conversation insights. Treat as factual prior context.\n{insights_text}"
        )

        state.messages = [insights_msg] + list(state.messages)
        return state

    def _persist_insights(self, state: AgentState) -> AgentState:
        existing_insights_bulleted = "\n".join(f"- {i}" for i in (state.insights or [])) if state.insights else "(none)"
        summarizer_system = SystemMessage(
            content=(
                "You are the Insights Summarizer for an Agent.\n"
                "Context: These insights will be injected as a SystemMessage before each future run of the same conversation/document.\n"
                "Goal: maximize future answer quality and tool choice by persisting information the next run should not have to re-derive.\n\n"
                "Include:\n"
                "- Stable facts about the document/domain and user preferences/constraints.\n"
                "- Key intermediate reasoning and tool outcomes (tool used, why, essential outputs/params, errors and proven workarounds).\n"
                "- Canonical entities/fields/mappings/definitions and computed values needed later.\n"
                "- Assumptions (and whether confirmed), open questions, and next best actions.\n\n"
                "Style: one insight per item, concise (<= 160 chars), specific, self-contained. Prefer including if in doubt; avoid trivial or redundant notes.\n\n"
                "Existing insights (avoid duplicates):\n"
                f"{existing_insights_bulleted}\n\n"
                "Output format: a JSON object with key 'insights' as an array of as many elements as needed."
            )
        )

        messages = [summarizer_system] + list(state.messages)

        structured = self.llm.with_structured_output(InsightsPayload).invoke(messages)

        extracted = [insight.strip() for insight in structured.insights]  # type: ignore

        if not extracted and not state.insights:
            return state

        merged = list(set(state.insights + extracted))
        state.insights = merged

        self._insights_store.save(state.conversation_id, state.tenant_id, merged)

        return state
