from dataclasses import dataclass

__all__ = ["OriginalImage"]


@dataclass
class OriginalImage:
    id: str
    page: int
    path: str
