from uuid import uuid4

import pytest


@pytest.fixture
def conversation_id() -> str:
    return uuid4().hex


@pytest.fixture
def tenant_id() -> str:
    return uuid4().hex


@pytest.fixture
def sample_insights() -> list[str]:
    return ["User prefers JSON format", "Document is invoice", "GPT-4 model used"]
