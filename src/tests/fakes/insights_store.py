from deps_ai_fusion.application import IInsightsStore

__all__ = ["InMemoryInsightsStore"]


class InMemoryInsightsStore(IInsightsStore):
    def __init__(self) -> None:
        self._storage: dict[tuple[str, str], list[str]] = {}

    def load(self, conversation_id: str, tenant_id: str) -> list[str]:
        return self._storage.get((conversation_id, tenant_id), [])

    def save(self, conversation_id: str, tenant_id: str, insights: list[str]) -> None:
        self._storage[(conversation_id, tenant_id)] = insights

    def delete_by_conversation_id(self, conversation_id: str) -> None:
        keys_to_delete = [key for key in self._storage if key[0] == conversation_id]
        for key in keys_to_delete:
            del self._storage[key]
