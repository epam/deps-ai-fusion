from typing import Protocol

__all__ = ["IInsightsStore"]


class IInsightsStore(Protocol):
    def load(self, conversation_id: str, tenant_id: str) -> list[str]:
        ...

    def save(self, conversation_id: str, tenant_id: str, insights: list[str]) -> None:
        ...

    def delete_by_conversation_id(self, conversation_id: str) -> None:
        ...
