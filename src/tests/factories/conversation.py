import factory
from faker import Faker

from deps_ai_fusion.domain.model.conversation import Conversation
from deps_ai_fusion.domain.model.conversation import (
    ConversationFactory as DomainFactory,
)

from .user_data import test_user_data

_fake = Faker()

__all__ = ["ConversationFactory"]


class ConversationFactory(factory.Factory):
    class Meta:
        model = Conversation

    entity_id: str = factory.LazyFunction(_fake.uuid4)
    user_id: str = factory.LazyFunction(lambda: test_user_data["subject"])
    tenant_id: str = factory.LazyFunction(lambda: test_user_data["organisation"])

    @classmethod
    def create(cls, **kwargs) -> Conversation:
        return DomainFactory.create(
            entity_id=kwargs["entity_id"].function(),
            user_id=kwargs["user_id"].function(),
            tenant_id=kwargs["tenant_id"].function(),
        )
