import json

import pytest

from deps_ai_fusion.domain.exceptions import BusinessError, QueryNotFoundError
from deps_ai_fusion.messaging.handlers import (
    conversation_deleted_handler,
    extractor_field_deleted_handler,
    perform_extraction_handler,
)


def test_perform_extraction__ok(mock_extraction_service, perform_llm_extraction_command):
    mock_extraction_service.perform_extraction.return_value = None

    reply = perform_extraction_handler(perform_llm_extraction_command)
    reply_payload = json.loads(reply[0].payload)

    assert reply_payload["error_type"] is None
    assert reply_payload["error_message"] is None


@pytest.mark.parametrize("error", [BusinessError, RuntimeError])
def test_perform_extraction__error_occured__error_in_reply(
    error,
    mock_extraction_service,
    perform_llm_extraction_command,
):
    mock_extraction_service.perform_extraction.side_effect = error

    reply = perform_extraction_handler(perform_llm_extraction_command)
    reply_payload = json.loads(reply[0].payload)

    assert reply_payload["error_type"] is not None
    assert reply_payload["error_message"] is not None


@pytest.mark.parametrize("error", [QueryNotFoundError, None])
def test_delete_query__ok(error, mock_extraction_service, extractor_field_deleted_event):
    mock_extraction_service.delete_query.return_value = None
    if error:
        mock_extraction_service.perform_extraction.side_effect = error

    reply = extractor_field_deleted_handler(extractor_field_deleted_event)

    assert reply is None


def test_conversation_deleted_handler__deletes_insights(
    conversation_deleted_event, fake_agent_service, fake_insights_store
):
    conversation_id = conversation_deleted_event.event.id
    tenant_id = "test-tenant"
    fake_insights_store.save(conversation_id=conversation_id, tenant_id=tenant_id, insights=["insight1", "insight2"])

    conversation_deleted_handler(
        dee=conversation_deleted_event,
        agent_service=fake_agent_service,
    )

    assert fake_insights_store.load(conversation_id=conversation_id, tenant_id=tenant_id) == []


def test_conversation_deleted_handler__handles_errors(mocker, conversation_deleted_event):
    mock_agent_service = mocker.Mock()
    mock_agent_service.delete_conversation_insights.side_effect = Exception("DB Error")

    with pytest.raises(Exception, match="DB Error"):
        conversation_deleted_handler(
            dee=conversation_deleted_event,
            agent_service=mock_agent_service,
        )

    mock_agent_service.delete_conversation_insights.assert_called_once()


def test_conversation_deleted_handler__idempotent(conversation_deleted_event, fake_agent_service, fake_insights_store):
    conversation_id = conversation_deleted_event.event.id
    tenant_id = "test-tenant"
    fake_insights_store.save(conversation_id=conversation_id, tenant_id=tenant_id, insights=["insight1"])

    for _ in range(2):
        conversation_deleted_handler(
            dee=conversation_deleted_event,
            agent_service=fake_agent_service,
        )

    assert fake_insights_store.load(conversation_id=conversation_id, tenant_id=tenant_id) == []
