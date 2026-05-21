from uuid import uuid4

from deps_gen_ai.providers import ProviderCode
from deps_message_flow.sagas.orchestration import SagaData

from deps_ai_fusion.domain.model import ContextAttachments, RawPageSpan

__all__ = ["CreateLLMExtractorSagaData"]


class CreateLLMExtractorSagaData(SagaData):
    def __init__(
        self,
        extractor_name: str,
        document_type_name: str,
        tenant_id: str,
        model: str,
        provider: ProviderCode,
        custom_instruction: str,
        grouping_factor: int,
        temperature: float,
        top_p: float,
        page_span: RawPageSpan | None,
        context_attachments: ContextAttachments | None,
        extractor_id: str | None = None,
    ) -> None:
        super().__init__(entity_id=uuid4().hex)
        self.extractor_name = extractor_name
        self.document_type_name = document_type_name
        self.tenant_id = tenant_id
        self.model = model
        self.provider = provider

        self.custom_instruction = custom_instruction
        self.grouping_factor = grouping_factor
        self.temperature = temperature
        self.top_p = top_p
        self.page_span = page_span
        self.context_attachments = context_attachments

        self.document_type_id: str | None = None
        self.extractor_id: str | None = extractor_id

        self._original_exc: Exception | None = None

    @property
    def original_exc(self) -> Exception | None:
        return self._original_exc

    @original_exc.setter
    def original_exc(self, value: Exception) -> None:
        self._original_exc = value
