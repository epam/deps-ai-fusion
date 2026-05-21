import http

from .base import AiFusionError

__all__ = ["AuthError"]


class AuthError(AiFusionError):
    code = "authentication_error"

    def __init__(self, detail: str, status_code: int = http.HTTPStatus.UNAUTHORIZED) -> None:
        super().__init__(detail)
        self.status_code = status_code
