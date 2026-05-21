from typing import Union

from deps_message_flow.sagas.orchestration import SagaInstance, SerializedSagaData
from sqlalchemy.engine.result import Result

__all__ = ["build_dict_from_saga_instance", "build_saga_instance_from_dict"]


def build_dict_from_saga_instance(saga_instance: SagaInstance) -> dict:
    return {
        "saga_type": saga_instance.saga_type,
        "saga_id": saga_instance.saga_id,
        "state_name": saga_instance.state_name,
        "last_request_id": saga_instance.last_request_id,
        "saga_data_type": saga_instance.serialized_saga_data.saga_data_type,
        "saga_data_json": saga_instance.serialized_saga_data.saga_data_json,
        "end_state": saga_instance.end_state,
        "compensating": saga_instance.compensating,
        "failed": saga_instance.failed,
    }


def build_saga_instance_from_dict(saga_dict: Union[dict, Result]) -> SagaInstance:
    return SagaInstance(
        saga_type=saga_dict["saga_type"],
        saga_id=saga_dict["saga_id"],
        state_name=saga_dict["state_name"],
        last_request_id=saga_dict["last_request_id"],
        serialized_saga_data=SerializedSagaData(
            saga_data_type=saga_dict["saga_data_type"],
            saga_data_json=saga_dict["saga_data_json"],
        ),
        end_state=saga_dict["end_state"],
        compensating=saga_dict["compensating"],
        failed=saga_dict["failed"],
    )
