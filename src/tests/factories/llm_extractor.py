import random

import factory
from deps_gen_ai.providers import ProviderCode
from faker import Faker

from deps_ai_fusion.domain.model import (
    Code,
    ContextAttachments,
    ExtractionParams,
    LLMExtractor,
    LLMReference,
    PageSpan,
    Query,
)

from .user_data import test_user_data

_fake = Faker()

__all__ = ["LLMExtractorFactory", "ExtractionParamsFactory", "LLMReferenceFactory", "PageSpanFactory"]


class PageSpanFactory(factory.Factory):
    class Meta:
        model = PageSpan

    start: int = factory.LazyFunction(lambda: _fake.random.randint(1, 5))
    end: int = factory.LazyFunction(lambda: _fake.random.randint(6, 10))


class ExtractionParamsFactory(factory.Factory):
    class Meta:
        model = ExtractionParams

    custom_instruction: str = factory.LazyFunction(_fake.uuid4)
    grouping_factor: int = factory.LazyFunction(lambda: _fake.random.randint(1, 50))
    temperature: float = factory.LazyFunction(lambda: _fake.random.random() * 2)
    top_p: float = factory.LazyFunction(_fake.random.random)
    page_span = factory.SubFactory(PageSpanFactory)
    context_attachments: str = factory.LazyFunction(lambda: random.choice(list(ContextAttachments)))


class LLMReferenceFactory(factory.Factory):
    class Meta:
        model = LLMReference

    provider: str = factory.LazyFunction(lambda: random.choice(list(ProviderCode)))
    model: str = factory.LazyFunction(_fake.pystr)


class LLMExtractorFactory(factory.Factory):
    class Meta:
        model = LLMExtractor

    id_: str = factory.LazyFunction(_fake.uuid4)
    tenant_id: str = factory.LazyFunction(lambda: test_user_data["organisation"])
    document_type_id: str = factory.LazyFunction(_fake.uuid4)
    name: str = factory.LazyFunction(_fake.pystr)

    extraction_params = factory.SubFactory(ExtractionParamsFactory)
    llm_reference = factory.SubFactory(LLMReferenceFactory)
    queries: dict[Code, Query] = {}
