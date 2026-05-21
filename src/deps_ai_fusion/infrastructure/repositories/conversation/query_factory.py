from sqlalchemy import Column, ColumnElement, and_, case, func, lateral, select, true
from sqlalchemy.dialects.postgresql import aggregate_order_by, insert
from sqlalchemy.sql import Insert, Select

from ...tables import conversation_table

__all__ = ["ConversationQueryFactory"]


class ConversationQueryFactory:
    def __init__(self) -> None:
        self.conversation_table = conversation_table

    @property
    def conversation_id_columns(self) -> list[Column]:
        return [
            self.conversation_table.c.entity_id,
            self.conversation_table.c.user_id,
            self.conversation_table.c.tenant_id,
        ]

    @property
    def completions(self) -> Column:
        return self.conversation_table.c.completions

    def ids_equality_condition(self, entity_id: str, user_id: str, tenant_id: str) -> ColumnElement[bool]:
        return and_(
            self.conversation_table.c.entity_id == entity_id,
            self.conversation_table.c.user_id == user_id,
            self.conversation_table.c.tenant_id == tenant_id,
        )

    def insert_conversation(self) -> Insert:
        query = insert(self.conversation_table)

        return query.on_conflict_do_update(
            index_elements=self.conversation_id_columns,
            set_=dict(query.excluded),
        )

    def select_conversation(self, entity_id: str, user_id: str, tenant_id: str) -> Select:
        """
        Returns a query to select a conversation by entity_id, user_id, and tenant_id
            with completions sorted by created_at in ascending order;
        In case conversation doesn't have completions, completions attribute will be `[]`;
        """

        completion_lateral = (
            lateral(
                select(
                    func.jsonb_array_elements(conversation_table.c.completions)
                    .label("completions_array"),
                )
                .where(
                    self.ids_equality_condition(
                        entity_id=entity_id, user_id=user_id, tenant_id=tenant_id,
                    ),
                )
                .select_from(conversation_table),
            )
        )

        completions_array = completion_lateral.c.completions_array
        aggregated_completions = func.jsonb_agg(
            aggregate_order_by(
                completions_array,
                completions_array.op("->>")("created_at").asc(),
            ),
        )

        return (
            select(
                *self.conversation_id_columns,
                case(
                    (aggregated_completions.op("=")(func.jsonb("[null]")), func.jsonb("[]")),
                    else_=aggregated_completions,
                )
                .label("sorted_completions"),
            )
            .select_from(self.conversation_table.outerjoin(completion_lateral, true()))
            .where(
                self.ids_equality_condition(
                    entity_id=entity_id, user_id=user_id, tenant_id=tenant_id,
                ),
            )
            .group_by(*self.conversation_id_columns)
        )
