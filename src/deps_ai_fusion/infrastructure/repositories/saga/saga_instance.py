from uuid import uuid4

from deps_message_flow.sagas.orchestration import ISagaInstanceRepository, SagaInstance
from sqlalchemy import insert, join, select, update

from deps_ai_fusion.domain.exceptions import NotFoundError
from deps_ai_fusion.extras import Database

from ...tables import entity_saga_pair_table, saga_table
from .mappers import build_dict_from_saga_instance, build_saga_instance_from_dict

__all__ = ["SagaInstanceRepository"]


class SagaInstanceRepository(ISagaInstanceRepository):
    def __init__(self, database: Database):
        self._db = database

    def save(self, saga_instance: SagaInstance) -> SagaInstance:
        saga_instance.saga_id = uuid4().hex
        query = insert(saga_table).values(build_dict_from_saga_instance(saga_instance))

        with self._db.connection() as connection:
            connection.execute(query)

        return saga_instance

    def find(self, saga_id: str) -> SagaInstance:
        query = select(saga_table).where(saga_table.c.saga_id == saga_id)

        with self._db.connection() as connection:
            saga_instance_row = connection.execute(query).fetchone()

        if not saga_instance_row:
            raise NotFoundError(f"Saga instance with saga_id = {saga_id} not found.")

        return build_saga_instance_from_dict(saga_instance_row)

    def update(self, saga_instance: SagaInstance) -> SagaInstance:
        fields_to_update = self._get_fields_to_update_from_saga_instance(saga_instance)

        query = (
            update(saga_table).where(saga_table.c.saga_id == saga_instance.saga_id).values(**fields_to_update)
        )  # noqa: WPS221

        with self._db.connection() as connection:
            connection.execute(query)

        return saga_instance

    def find_for_entity(self, entity_id: str) -> SagaInstance:
        joined_tables = join(
            entity_saga_pair_table,
            saga_table,
            entity_saga_pair_table.c.saga_id == saga_table.c.saga_id,
        )
        query = select(saga_table).select_from(joined_tables).where(entity_saga_pair_table.c.entity_id == entity_id)

        with self._db.connection() as connection:
            saga_instance_row = connection.execute(query).fetchone()

        if not saga_instance_row:
            raise NotFoundError(f"Saga instance for entity with id = {entity_id} not found.")

        return build_saga_instance_from_dict(saga_instance_row)

    @staticmethod
    def _get_fields_to_update_from_saga_instance(saga_instance: SagaInstance) -> dict:
        fields_to_update = build_dict_from_saga_instance(saga_instance)
        del fields_to_update["saga_id"]

        return fields_to_update
