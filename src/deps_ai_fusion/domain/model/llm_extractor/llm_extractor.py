from deps_message_flow.events.common import DomainEvent

from ...events import ExtractionFieldsMoved
from ...exceptions import QueryAlreadyExistsError, QueryNotFoundError
from ..shared import (
    EntityId,
    Guard,
    ImmutableCheck,
    LengthCheck,
    LLMReference,
    TenantId,
)
from .extraction_params.extraction_params import ExtractionParams
from .query import (
    Code,
    DataShape,
    LLMExecutionNode,
    LLMWorkflow,
    Query,
    RawDataShape,
    RawLLMWorkflow,
    SequentialEdge,
)
from .raw_extraction_params import RawLLMExtractionParams

__all__ = ["LLMExtractor"]


class LLMExtractor:
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 255
    MIN_MODEL_LENGTH = 1

    id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    document_type_id = Guard[EntityId](EntityId, ImmutableCheck())
    llm_reference = Guard[LLMReference](LLMReference)
    name = Guard[str](str, LengthCheck(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH))
    queries = Guard[dict[Code, Query]](dict, ImmutableCheck())
    extraction_params = Guard[ExtractionParams](ExtractionParams)

    def __init__(
        self,
        id_: str,
        tenant_id: str,
        document_type_id: str,
        llm_reference: LLMReference,
        name: str,
        queries: dict[Code, Query],
        extraction_params: ExtractionParams,
        events: list[DomainEvent] | None = None,
    ) -> None:
        self.id = EntityId(id_)
        self.tenant_id = TenantId(tenant_id)
        self.document_type_id = EntityId(document_type_id)
        self.llm_reference = llm_reference
        self.name = name
        self.queries = queries
        self.extraction_params = extraction_params
        self._events: list[DomainEvent] = events or []

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LLMExtractor) and other.id == self.id

    def __repr__(self) -> str:
        return (
            f"LLMExtractor(id={self.id!r}, tenant_id={self.tenant_id!r}, "
            f"document_type_id={self.document_type_id!r}, llm_reference={self.llm_reference!r}, "
            f"name={self.name!r}, queries={self.queries!r}, extraction_params={self.extraction_params!r})"
        )

    def __str__(self) -> str:
        return (
            f"LLMExtractor: {self.name} (ID: {self.id}, Tenant: {self.tenant_id}, "
            f"Document Type: {self.document_type_id}, LLM: {self.llm_reference.provider} - {self.llm_reference.model})"
        )

    @property
    def has_queries(self) -> bool:
        return bool(self.queries)

    def query_values(self) -> list[Query]:
        return list(self.queries.values())

    def add_query(self, code: Code, workflow: RawLLMWorkflow, data_shape: RawDataShape) -> Query:
        if code in self.queries:
            raise QueryAlreadyExistsError(code=code, extractor_id=self.id(), tenant_id=self.tenant_id())

        query_object = Query(
            code=code,
            workflow=LLMWorkflow(
                entrypoint_node_id=workflow["start_node_id"],
                output_node_id=workflow["end_node_id"],
                nodes=[
                    LLMExecutionNode(id_=node["id"], name=node["name"], prompt=node["prompt"])
                    for node in workflow["nodes"]
                ],
                edges=[
                    SequentialEdge(source_id=edge["source_id"], target_id=edge["target_id"])
                    for edge in workflow["edges"]
                ],
            ),
            shape=DataShape(
                data_type=data_shape["data_type"],
                cardinality=data_shape["cardinality"],
                include_aliases=data_shape["include_aliases"],
            ),
        )
        self.queries[code] = query_object

        return query_object

    def update_query(self, code: str, workflow: RawLLMWorkflow) -> Query:
        if code not in self.queries:
            raise QueryNotFoundError(code=code, extractor_id=self.id(), tenant_id=self.tenant_id())

        self.queries[code].update(workflow)

        return self.queries[code]

    def delete_query(self, code: Code) -> Query:
        if code not in self.queries:
            raise QueryNotFoundError(code=code, extractor_id=self.id(), tenant_id=self.tenant_id())

        return self.queries.pop(code)

    def update(
        self,
        params: RawLLMExtractionParams,
        name: str,
    ) -> "LLMExtractor":
        self.name = name
        self.extraction_params = self.extraction_params.create_updated(
            custom_instruction=params["custom_instruction"],
            grouping_factor=params["grouping_factor"],
            temperature=params["temperature"],
            top_p=params["top_p"],
            page_span=params["page_span"],
            context_attachments=params["context_attachments"],
        )

        return self

    def assign_llm(self, provider: str, model: str) -> "LLMExtractor":
        self.llm_reference = self.llm_reference.create_updated(provider=provider, model=model)
        return self

    def move_query_from(self, from_extractor: "LLMExtractor", fields_codes: list) -> None:
        for code in fields_codes:
            if code not in from_extractor.queries:
                raise QueryNotFoundError(code, from_extractor.id(), from_extractor.tenant_id())
            if code in self.queries:
                raise QueryAlreadyExistsError(code=code, extractor_id=self.id(), tenant_id=self.tenant_id())

            query = from_extractor.queries.get(code)
            self.queries[code] = query
            from_extractor.delete_query(code)

        self._events.append(
            ExtractionFieldsMoved(
                document_type_id=from_extractor.document_type_id(),
                source_extractor_id=from_extractor.id(),
                target_extractor_id=self.id(),
                fields_codes=fields_codes,
            ),
        )

    @property
    def events(self) -> list[DomainEvent]:
        return self._events

    def drain_events(self) -> list[DomainEvent]:
        events = self._events
        self._events = []

        return events
