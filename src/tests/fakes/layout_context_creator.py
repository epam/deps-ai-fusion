from deps_gen_ai.common import ContextReference
from deps_gen_ai.context_creators import PlainLayoutContextCreator

__all__ = ["FakePlainLayoutContextCreator"]


class FakePlainLayoutContextCreator(PlainLayoutContextCreator):
    def __init__(self) -> None:
        # Don't call super().__init__ to avoid needing real loader
        self._context_responses: dict[str, str] = {}

    def context_of(self, context: ContextReference) -> str:
        entity_id = context.entity_id or "default"
        return self._context_responses.get(entity_id, f"Fake context for {entity_id}")

    def set_context_response(self, entity_id: str, response: str) -> None:
        self._context_responses[entity_id] = response
