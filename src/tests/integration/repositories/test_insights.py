from uuid import uuid4

import pytest

from deps_ai_fusion.infrastructure.repositories import InsightsRepository


def test_save_and_load_insights(
    insights_repository: InsightsRepository,
    conversation_id: str,
    tenant_id: str,
    sample_insights: list[str],
) -> None:
    loaded_insights = insights_repository.load(conversation_id, tenant_id)
    assert loaded_insights == []

    insights_repository.save(conversation_id, tenant_id, sample_insights)

    loaded_insights = insights_repository.load(conversation_id, tenant_id)
    assert loaded_insights == sample_insights


def test_load_nonexistent_insights(
    insights_repository: InsightsRepository,
    conversation_id: str,
    tenant_id: str,
) -> None:
    loaded_insights = insights_repository.load(conversation_id, tenant_id)
    assert loaded_insights == []


def test_save_empty_insights(
    insights_repository: InsightsRepository,
    conversation_id: str,
    tenant_id: str,
) -> None:
    insights_repository.save(conversation_id, tenant_id, [])
    loaded_insights = insights_repository.load(conversation_id, tenant_id)
    assert loaded_insights == []


def test_update_insights(
    insights_repository: InsightsRepository,
    conversation_id: str,
    tenant_id: str,
    sample_insights: list[str],
) -> None:
    insights_repository.save(conversation_id, tenant_id, sample_insights)
    updated_insights = ["New insight 1", "New insight 2"]
    insights_repository.save(conversation_id, tenant_id, updated_insights)

    loaded_insights = insights_repository.load(conversation_id, tenant_id)
    assert loaded_insights == updated_insights
