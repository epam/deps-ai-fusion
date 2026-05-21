from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import Response

from deps_ai_fusion import api
from deps_ai_fusion.api.error_handlers import json_ai_fusion_error_handler
from deps_ai_fusion.domain.exceptions import AuthError

__all__ = ["register_auth"]


def register_auth(app: FastAPI) -> None:
    api.add_auth_to_openapi(app)

    @app.middleware("http")
    async def handle_authorization(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            api.auth.set_user_from_token(request)
        except AuthError as err:
            return json_ai_fusion_error_handler(err, err.status_code)

        return await call_next(request)
