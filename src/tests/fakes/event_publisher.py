from deps_message_flow.events.common import DomainEvent

__all__ = ["FakeEventPublisher"]


class FakeEventPublisher:
    def __init__(self) -> None:
        self.published_events: list[DomainEvent] = []
        self.published_events_with_type_and_id: list[tuple[str, str, DomainEvent]] = []

    def publish(
        self, aggregate_type: str, aggregate_id: str, domain_events: list[DomainEvent], *, headers: dict[str, str] = {}
    ) -> None:
        for event in domain_events:
            self.published_events.append(event)
            self.published_events_with_type_and_id.append((aggregate_type, aggregate_id, event))

    def reset(self):
        self.__init__()
