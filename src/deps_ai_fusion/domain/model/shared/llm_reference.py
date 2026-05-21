from . import Guard, ImmutableCheck

__all__ = ["LLMReference"]


class LLMReference:
    provider = Guard[str](str, ImmutableCheck())
    model = Guard[str](str, ImmutableCheck())

    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LLMReference) and self.provider == other.provider and self.model == other.model

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.provider = },",
                f"{self.model = },",
            ),
        )

    def create_updated(self, provider: str, model: str) -> "LLMReference":
        return LLMReference(provider=provider, model=model)
