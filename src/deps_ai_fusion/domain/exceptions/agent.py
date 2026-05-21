from .base import AiFusionError

__all__ = ["RequiredArgumentMissing"]


class RequiredArgumentMissing(AiFusionError):
    code = "required_argument_missing"
