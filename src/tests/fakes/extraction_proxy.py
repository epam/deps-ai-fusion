from typing import Any, Literal

from deps_ai_fusion.infrastructure.proxies import ExtractionProxy
from deps_ai_fusion.infrastructure.proxies.types import AttachmentInfo

__all__ = ["FakeExtractionProxy"]


class FakeExtractionProxy(ExtractionProxy):
    def __init__(self) -> None:
        # Don't call super().__init__ to avoid needing real URL/timeout
        self._created_fields: dict[str, str] = {}
        self._create_field_calls: list[dict[str, Any]] = []
        self._create_field_return_value: str | None = None

    def attach_extractor(
        self,
        document_type_name: str,
        extractor_type: str,
        extractor_id: str | None,
    ) -> AttachmentInfo:
        return AttachmentInfo(document_type_id="fake-doc-type-id", extractor_id="fake-extractor-id")

    def detach_extractor(self, document_type_id: str, extractor_id: str) -> None:
        pass

    def save_extracted_data(self, extracted_data: Any) -> None:
        pass

    def create_extraction_field(
        self,
        document_type_id: str,
        extractor_id: str,
        name: str,
        type_: Literal["string", "checkmark", "dict", "list"],
        description: dict[str, Any] | None,
    ) -> str:
        # Track the call
        self._create_field_calls.append(
            {
                "document_type_id": document_type_id,
                "extractor_id": extractor_id,
                "name": name,
                "type_": type_,
                "description": description,
            }
        )

        if self._create_field_return_value is not None:
            field_code = self._create_field_return_value
        else:
            field_code = f"fake-field-{len(self._created_fields)}"

        self._created_fields[field_code] = name
        return field_code

    def assert_create_field_called(self) -> None:
        assert len(self._create_field_calls) > 0, "create_extraction_field was not called"

    def assert_create_field_called_with(self, **kwargs) -> None:
        for call in self._create_field_calls:
            if all(call.get(key) == value for key, value in kwargs.items()):
                return
        raise AssertionError(f"create_extraction_field was not called with {kwargs}")

    def get_create_field_calls(self) -> list[dict[str, Any]]:
        return self._create_field_calls.copy()

    def set_create_field_return_value(self, return_value: str) -> None:
        """Set the return value for create_extraction_field calls."""
        self._create_field_return_value = return_value
