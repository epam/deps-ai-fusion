import factory
from faker import Faker

from deps_ai_fusion.infrastructure.agent.state import AgentState

__all__ = ["AgentStateFactory"]


_fake = Faker()


class AgentStateFactory(factory.Factory):
    class Meta:
        model = AgentState

    conversation_id: str = factory.LazyFunction(_fake.uuid4)
    tenant_id: str = factory.LazyFunction(_fake.uuid4)
    document_id: str = factory.LazyFunction(_fake.uuid4)
    document_type_id = None
    extractor_id = None
    insights: list[str] = []
    messages: list = []
