import logging
from http import HTTPStatus

from deps_gen_ai import exceptions as ai_exceptions
from deps_gen_ai.exceptions import InvalidPageSpan, ModelNotFound
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.requests import Request

from deps_ai_fusion.api.serializers.error import ErrorSerializer
from deps_ai_fusion.domain.exceptions import *

logger = logging.getLogger(__name__)


def json_ai_fusion_error_handler(error: AiFusionError, status_code: int):
    error_message = ErrorSerializer(code=error.code, message=str(error)).model_dump()
    return JSONResponse(status_code=status_code, content=error_message)


def register_error_handler(app: FastAPI) -> None:
    @app.exception_handler(AiFusionError)
    def handle_ai_fusion_exception(req: Request, error: AiFusionError):  # noqa: WPS430
        mapper = [
            (NotFoundError, HTTPStatus.NOT_FOUND),
            (ai_exceptions.NotFoundError, HTTPStatus.NOT_FOUND),
            (AlreadyExistsError, HTTPStatus.CONFLICT),
            (AiFusionError, HTTPStatus.BAD_REQUEST),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_ai_fusion_error_handler(error, status_code)

    @app.exception_handler(ModelNotFound)
    def model_not_found(req: Request, exc: ModelNotFound):  # noqa: WPS430
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=ErrorSerializer(code=exc.code, message=str(exc)).model_dump(),
        )

    @app.exception_handler(InvalidPageSpan)
    def bad_page_span(req: Request, exc: InvalidPageSpan):  # noqa: WPS430
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorSerializer(code=exc.code, message=str(exc)).model_dump(),
        )

    @app.exception_handler(ValidationError)
    def bad_request(req: Request, exc: ValidationError):  # noqa: WPS430
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorSerializer(code="bad_request", message=str(exc)).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(req: Request, error: Exception):  # noqa: WPS430
        logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=ErrorSerializer(code="unhandled_error", message=str(error)).model_dump(),
        )
