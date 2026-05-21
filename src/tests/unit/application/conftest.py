from unittest.mock import Mock

import pytest

from deps_ai_fusion.infrastructure.agent import AgentRegistrator, GenAIQueriesAgent


@pytest.fixture
def mock_workflow_factory():
    mock = Mock()
    mock.available_tools.return_value = [{"code": "test-tool", "name": "Test Tool", "parameters": []}]
    return mock


@pytest.fixture
def agent_registrator():
    return AgentRegistrator(
        agentic_ai_proxy=Mock(),
        meta_agent_proxy=Mock(),
    )


@pytest.fixture
def genai_agent(mock_workflow_factory, agent_registrator):
    return GenAIQueriesAgent(
        workflow_factory=mock_workflow_factory,
        agent_registrator=agent_registrator,
    )
