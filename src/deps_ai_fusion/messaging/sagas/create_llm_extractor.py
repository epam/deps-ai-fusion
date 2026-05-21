import logging

from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from .sagas_data import CreateLLMExtractorSagaData, CreateLLMExtractorSteps

__all__ = ["CreateLLMExtractorSaga"]


class CreateLLMExtractorSaga(SimpleSaga[CreateLLMExtractorSagaData]):
    def __init__(self, steps: CreateLLMExtractorSteps) -> None:
        # fmt: off
        self._saga_definition = (
            self.step()
            .invoke_local(steps.attach_extractor)
            .with_compensation(steps.detach_extractor)
            .step()
            .invoke_local(steps.create_extractor)
            .build()
        )
        # fmt: on
        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: CreateLLMExtractorSagaData) -> None:
        self._logger.info("CreateLLMExtractorgSaga: %s is completed successfully", saga_id)

    def on_saga_failed(self, saga_id: str, data: CreateLLMExtractorSagaData) -> None:
        self._logger.error("CreateLLMExtractorgSaga: %s is failed", saga_id)

    def on_saga_rolled_back(self, saga_id: str, data: CreateLLMExtractorSagaData) -> None:
        self._logger.error("CreateLLMExtractorgSaga: %s is rolled back", saga_id)
