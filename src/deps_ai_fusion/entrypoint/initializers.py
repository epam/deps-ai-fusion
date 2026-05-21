import logging

from deps_gen_ai import init_providers_aggregate
from fastapi import FastAPI

from deps_ai_fusion import api, messaging
from deps_ai_fusion.api.error_handlers import register_error_handler
from deps_ai_fusion.containers import Containers
from deps_ai_fusion.infrastructure.access_management import user
from deps_ai_fusion.settings import Settings

from .auth import register_auth

__all__ = ["init_containers", "base_service_init", "fastapi_post_initialization"]

_logger = logging.getLogger(__name__)


def init_containers(settings: Settings) -> Containers:
    containers = Containers(
        messaging_driver_settings=settings.messaging_driver_settings,
        providers_aggregate=init_providers_aggregate(user_context=user),
    )

    containers.config.from_dict(settings.model_dump())
    containers.init_resources()
    containers.wire(
        packages=[api, messaging],
    )

    containers.message_brokers.broker_client().user_context = user

    containers.core.wire(
        modules=[api.endpoints.service_info],
    )
    containers.datasources.wire(
        modules=[api.endpoints.healthcheck],
    )

    return containers


def base_service_init(containers: Containers) -> None:
    if containers.config.instrumentation_enabled():
        _logger.info("Instrumentation enabled.")
        from deps_observability_instrumentation import (  # noqa: WPS433
            instrument_messaging,
            setup_instrumentation,
        )

        setup_instrumentation()
        instrument_messaging(containers.messaging.producer(), containers.messaging.consumer())


def fastapi_post_initialization(fastapi_app: FastAPI, containers: Containers) -> FastAPI:
    fastapi_app.containers = containers

    register_auth(fastapi_app)
    register_error_handler(fastapi_app)

    if containers.config.instrumentation_enabled():
        from deps_observability_instrumentation import (  # noqa: WPS433
            instrument_fast_api,
        )

        instrument_fast_api(fastapi_app)

    return fastapi_app
