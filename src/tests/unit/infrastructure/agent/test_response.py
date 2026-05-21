import json

from langchain_core.messages import AIMessage, ToolMessage

from deps_ai_fusion.infrastructure.agent import AgentChunk


def test_agent_chunk_supports_false_when_no_messages_key() -> None:
    assert AgentChunk.supports({}) is False


def test_agent_chunk_supports_true_for_ai_message() -> None:
    chunk = {"messages": [AIMessage(content="hi")]}
    assert AgentChunk.supports(chunk) is True


def test_agent_chunk_supports_true_for_tool_message() -> None:
    chunk = {"messages": [ToolMessage(content="ok", name="tool", tool_call_id="1")]}
    assert AgentChunk.supports(chunk) is True


def test_agent_chunk_from_ai_message_with_tool_call_parses_reasoning_json() -> None:
    arguments = json.dumps({"reasoning": "because"})
    msg = AIMessage(
        content="",
        additional_kwargs={
            "tool_calls": [
                {
                    "id": "1",
                    "type": "function",
                    "function": {"name": "tool", "arguments": arguments},
                },
            ],
        },
    )

    chunk = AgentChunk.from_langchain_message(msg)

    assert chunk.type_ == "ToolCall"
    assert "I have to call 'tool'" in chunk.text
    assert "because" in chunk.text


def test_agent_chunk_from_ai_message_with_tool_call_handles_invalid_json() -> None:
    msg = AIMessage(
        content="",
        additional_kwargs={
            "tool_calls": [
                {
                    "id": "1",
                    "type": "function",
                    "function": {"name": "tool", "arguments": "{not-json}"},
                }
            ]
        },
    )

    chunk = AgentChunk.from_langchain_message(msg)

    assert chunk.type_ == "ToolCall"
    assert "{not-json}" in chunk.text


def test_agent_chunk_from_plain_ai_message_is_final() -> None:
    msg = AIMessage(content="final answer")
    chunk = AgentChunk.from_langchain_message(msg)

    assert chunk.type_ == "Final"
    assert chunk.text == "final answer"


def test_agent_chunk_from_tool_message() -> None:
    msg = ToolMessage(content="ok", name="calc", tool_call_id="1", status="success")
    chunk = AgentChunk.from_langchain_message(msg)

    assert chunk.type_ == "ToolCallResponse"
    assert "Tool calc responded with success" in chunk.text
