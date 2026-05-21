from typing import Annotated

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic

from deps_ai_fusion.application.types import RawAgentArguments, RawContextBundle
from deps_ai_fusion.domain.exceptions import RequiredArgumentMissing
from deps_ai_fusion.infrastructure.access_management import user

__all__ = ["AgentState"]


def keep_last(previous: str | None, new: str | None) -> str | None:
    return new if new is not None else previous


class AgentState(AgentStatePydantic):
    conversation_id: str
    tenant_id: str
    document_id: str
    document_type_id: str | None = None
    extractor_id: Annotated[str | None, keep_last] = None
    insights: list[str] = []

    @classmethod
    def from_arguments(
        cls,
        conversation_id: str,
        args: RawAgentArguments,
        context: RawContextBundle,
        question: str,
    ) -> "AgentState":
        if "document_id" not in args:
            raise RequiredArgumentMissing("Document ID is a required argument for the agent!")
        if (tenant_id := user.get()["organisation"]) is None:
            raise RequiredArgumentMissing("Tenant ID is a required argument for the agent!")

        document_id = args["document_id"][0]["value"]
        document_type_id = args["document_type_id"][0]["value"] if "document_type_id" in args else None

        conversation_trim: list[HumanMessage | AIMessage] = []
        for msg in context["conversation_trim"]:
            conversation_trim.append(HumanMessage(content=msg["question"]))
            conversation_trim.append(AIMessage(content=msg["answer"]))

        conversation_trim.append(HumanMessage(content=question))

        return cls(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            document_id=document_id,
            document_type_id=document_type_id,
            messages=conversation_trim,
        )
