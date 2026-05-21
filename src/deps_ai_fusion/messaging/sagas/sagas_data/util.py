# flake8: noqa
from deps_message_flow.sagas.orchestration import SagaData, SagaDataMapping

__all__ = ["make_saga_data_mapping"]


def make_saga_data_mapping() -> SagaDataMapping:
    return SagaDataMapping(
        {
            SagaData.__name__: SagaData,
        }
    )
