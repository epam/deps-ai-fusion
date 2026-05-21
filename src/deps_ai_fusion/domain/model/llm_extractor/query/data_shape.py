from ....exceptions import InvariantViolationError
from ...shared import Guard, ImmutableCheck
from .cardinality import Cardinality
from .data_type import DataType

__all__ = ["DataShape"]


class DataShape:
    data_type = Guard[DataType](DataType, ImmutableCheck())
    cardinality = Guard[Cardinality](Cardinality, ImmutableCheck())
    include_aliases = Guard[bool](bool, ImmutableCheck())

    def __init__(self, data_type: DataType, cardinality: Cardinality, include_aliases: bool = False) -> None:
        self.data_type = data_type
        self.cardinality = cardinality

        self.include_aliases = include_aliases

        self._validate()

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DataShape)
            and other.data_type == self.data_type
            and other.cardinality == self.cardinality
            and other.include_aliases == self.include_aliases
        )

    def __repr__(self) -> str:
        return (
            f"DataShape(data_type={self.data_type!r}, "
            f"cardinality={self.cardinality!r}, "
            f"include_aliases={self.include_aliases!r})"
        )

    def __str__(self) -> str:
        return (
            f"DataShape with data_type={self.data_type}, "
            f"cardinality={self.cardinality}, "
            f"include_aliases={'enabled' if self.include_aliases else 'disabled'}"
        )

    def _validate(self) -> None:
        if self.include_aliases and self.cardinality != Cardinality.LIST:
            raise InvariantViolationError(
                f"include_aliases attrubutute is not applicable for DataShape with cardinality: {self.cardinality}",
            )
