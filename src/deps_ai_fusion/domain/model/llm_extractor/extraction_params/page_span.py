from typing import Any

from deps_ai_fusion.domain.model.shared import Guard, ImmutableCheck, RangeCheck

__all__ = ["PageSpan"]


class PageSpan:
    start = Guard[int](int, ImmutableCheck(), RangeCheck(min_value=1))
    end = Guard[int](int, ImmutableCheck(), RangeCheck(min_value=1))

    def __init__(self, start: int, end: int) -> None:
        if start > end:
            raise ValueError("PageSpan start must be less or equal end!")

        self.start = start
        self.end = end

    def __contains__(self, page: int) -> bool:
        return self.start <= page <= self.end

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PageSpan):
            return NotImplemented
        return (self.start, self.end) == (other.start, other.end)

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __repr__(self) -> str:
        return f"PageSpan(start={self.start}, end={self.end})"

    def to_dict(self):
        return {"start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, raw_data: dict | Any) -> "PageSpan":
        return cls(start=raw_data.get("start"), end=raw_data.get("end"))
