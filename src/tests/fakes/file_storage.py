from typing import Any

__all__ = ["FakeFileStorage"]


class FakeFileStorage:
    def __init__(self) -> None:
        self._response = b""

    def download_content(self, filepath: str) -> bytes:
        return self._response

    def set_bytes_response(self, data: bytes) -> None:
        self._response = data
