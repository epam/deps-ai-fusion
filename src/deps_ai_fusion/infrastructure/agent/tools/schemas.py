from typing import Annotated

from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel, Field

from deps_ai_fusion.domain.model import Cardinality, DataType

from ..state import AgentState

__all__ = ["ExecuteLLMExtractionRequest", "CreateGenAIFieldRequest", "DataShape"]


class DataShape(BaseModel):
    data_type: DataType = Field(
        description="Atomic type of the extracted value(s). Examples: STRING, BOOLEAN, KEY_VALUE_PAIR.",
    )
    cardinality: Cardinality = Field(
        description="Expected number of values: SCALAR for a single value, LIST for multiple values.",
    )
    include_aliases: bool = Field(
        False,
        description="Available only for list cardinality."
        " If True, then name/title for each element of list will be extracted.",
    )


class CreateGenAIFieldRequest(BaseModel):
    reasoning: str = Field(
        description="Brief rationale (<=20 words) for creating the field now, including user approval.",
    )
    name: str = Field(
        description="Human-readable, plain format field name unique within the Document Type.",
        examples=["Invoice Total", "Vendor Name", "Line Items"],
    )
    prompts_chain: list[str] = Field(
        description="Ordered prompts forming the extraction workflow; each prompt is a clear, atomic step."
        " Output of each prompt is used as input for the next prompt. Last prompt should return the desired response."
        " Don't overengineer the prompts chain, if you think that one prompt is enough, then use only one prompt.",
    )
    response_model: DataShape = Field(description="Desired response structure for the field.")

    state: Annotated[AgentState, InjectedState()]
    tool_call_id: Annotated[str, InjectedToolCallId()]


class ExecuteLLMExtractionRequest(BaseModel):
    reasoning: str = Field(description="Short hypothesis for this test (<=20 words).")
    prompts_chain: list[str] = Field(description="Ordered prompts to run for this test.")
    response_model: DataShape = Field(description="Expected output shape for the test run.")

    state: Annotated[AgentState, InjectedState()]
    tool_call_id: Annotated[str, InjectedToolCallId()]


class DocumentTypeCreationRequest(BaseModel):
    reasoning: str = Field(description="Reason for creating the document type.")
    document_type_name: str = Field(description="Name of the document type to create.")

    tool_call_id: Annotated[str, InjectedToolCallId()]
    state: Annotated[AgentState, InjectedState()]
