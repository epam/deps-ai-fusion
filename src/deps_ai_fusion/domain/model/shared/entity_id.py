from .guards import Guard, ImmutableCheck

__all__ = ["EntityId"]


class EntityId:
    value = Guard[str](str, ImmutableCheck())

    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EntityId) and self.value == other.value

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': {self.value = }>"
