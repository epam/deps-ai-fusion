from typing import Any

from pydantic import Field

from deps_ai_fusion.application.types import (
    RawAgentArgument,
    RawAgentArguments,
    RawContextBundle,
)

from ..base import ConfiguredBaseModel

__all__ = ["AgentRequest"]


class Argument(ConfiguredBaseModel):
    value: Any

    def to_raw(self) -> RawAgentArgument:
        return {"value": self.value}


class Completion(ConfiguredBaseModel):
    question: str
    answer: str


class ContextBundle(ConfiguredBaseModel):
    conversation_trim: list[Completion] = Field(..., alias="conversationTrim")

    def to_raw(self) -> RawContextBundle:
        return {
            "conversation_trim": [
                {"question": completion.question, "answer": completion.answer} for completion in self.conversation_trim
            ],
        }


class AgentRequest(ConfiguredBaseModel):
    conversation_id: str = Field(..., alias="conversationId")
    turn_id: str = Field(..., alias="turnId", description="Completion ID in Agentic AI Service")
    user_question: str = Field(..., alias="userQuestion")
    context_bundle: ContextBundle = Field(..., alias="contextBundle")
    arguments: dict[str, list[Argument]] = Field(
        ...,
        alias="arguments",
        description="Mapping between a registered toolCode and its arguments",
    )

    def raw_arguments(self) -> RawAgentArguments:
        return {code: [argument.to_raw() for argument in args] for code, args in self.arguments.items()}

    def raw_context_bundle(self) -> RawContextBundle:
        return self.context_bundle.to_raw()
