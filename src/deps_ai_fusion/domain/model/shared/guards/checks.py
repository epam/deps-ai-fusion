import re
from typing import Any, Optional, Protocol, Sized, Type, TypeVar, Union

from ....exceptions import IllegalArgument
from .attribute_name import AttributeName

T = TypeVar("T", contravariant=True)

__all__ = ["Check", "NoneCheck", "TypeCheck", "ImmutableCheck", "LengthCheck", "FormatCheck", "RangeCheck"]


class Check(Protocol[T]):
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        ...  # noqa: WPS428


class NoneCheck:
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if value is None:
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object should be provided.",
            )


class TypeCheck:
    def __init__(self, type_: Type[T]) -> None:
        self._type = type_

    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if not isinstance(value, self._type):
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object "
                f"should be {self._type.__name__}.",  # noqa: WPS326
            )


class ImmutableCheck:
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if hasattr(domain_obj, attribute_name.private) and getattr(domain_obj, attribute_name.private) is not None:
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object cannot be changed.",
            )


class LengthCheck:
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None) -> None:
        self._min_length = min_length
        self._max_length = max_length

    def is_correct(self, domain_obj: Any, value: Sized, attribute_name: AttributeName) -> None:
        if self._max_length is not None and len(value) > self._max_length:
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object cannot be more "
                f"than {self._max_length}.",
            )

        if self._min_length is not None and len(value) < self._min_length:
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object cannot be less "
                f"than {self._min_length}.",
            )


class FormatCheck:
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern

    def is_correct(self, domain_obj: Any, value: str, attribute_name: AttributeName) -> None:
        if not re.fullmatch(self._pattern, value):
            raise IllegalArgument(
                (
                    "Attribute {0} for {1} object should not contain special symbols.".format(
                        attribute_name.public,
                        domain_obj.__class__.__name__,
                    )
                ),
            )


class RangeCheck:
    def __init__(self, min_value: Union[int, float, None] = None, max_value: Union[int, float, None] = None) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def is_correct(self, domain_obj: Any, value: Union[int, float], attribute_name: AttributeName) -> None:
        if self._min_value is not None and value < self._min_value:
            raise IllegalArgument(
                (
                    "Attribute {0} for {1} object should be large than {2}.".format(
                        attribute_name.public,
                        domain_obj.__class__.__name__,
                        self._min_value,
                    )
                ),
            )
        if self._max_value is not None and value > self._max_value:
            raise IllegalArgument(
                (
                    "Attribute {0} for {1} object should be smaller than {2}.".format(
                        attribute_name.public,
                        domain_obj.__class__.__name__,
                        self._max_value,
                    )
                ),
            )
