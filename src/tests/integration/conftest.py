import pytest

from deps_ai_fusion.containers import Containers
from deps_ai_fusion.domain.model import LLMExtractor
from deps_ai_fusion.infrastructure.repositories import (
    ConversationRepository,
    InsightsRepository,
    LLMExtractorRepository,
)


@pytest.fixture
def conversation_repository(repositories: Containers) -> ConversationRepository:
    return repositories.conversation_repository()


@pytest.fixture
def llm_extractor_repository(repositories: Containers) -> LLMExtractorRepository:
    return repositories.llm_extractor_repository()


@pytest.fixture
def insights_repository(repositories: Containers) -> InsightsRepository:
    return repositories.insights_repository()


@pytest.fixture
def test_saved_llm_extractor(llm_extractor_repository, llm_extractor) -> LLMExtractor:
    llm_extractor_repository.save(llm_extractor)
    return llm_extractor
