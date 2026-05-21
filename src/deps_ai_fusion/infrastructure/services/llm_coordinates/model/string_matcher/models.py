from dataclasses import dataclass

from .types import BaseCases, IndexCost


class QueryWord:
    def __init__(
        self,
        value: str,
        position: int,
        index_cost: BaseCases | IndexCost | None = None,
        invalid_left_string: bool | None = False,
        invalid_right_string: bool | None = False,
    ):
        self.value = value
        self.position = position
        self.index_cost = index_cost if index_cost is not None else {}
        self.optimal_index = None
        self.invalid_left_string = invalid_left_string
        self.invalid_right_string = invalid_right_string
