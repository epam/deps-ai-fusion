import contextvars
from typing import Optional

__all__ = ["user"]

UserDict = dict[str, Optional[str]]

user: contextvars.ContextVar[UserDict] = contextvars.ContextVar("user")
