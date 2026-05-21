import logging

from fastapi import FastAPI

from deps_ai_fusion import api, constants
from deps_ai_fusion.containers import Containers
from deps_ai_fusion.settings import Settings

from .initializers import (
    base_service_init,
    fastapi_post_initialization,
    init_containers,
)

__all__ = ["create_fastapi", "create_agent_fastapi"]

_logger = logging.getLogger(__name__)


def create_fastapi() -> FastAPI:
    settings = Settings()
    containers: Containers = init_containers(settings)
    base_service_init(containers)

    fastapi_app = FastAPI(
        title=constants.PROJECT_NAME,
        version=containers.config.version(),
        docs_url=f"{constants.V1_API_PREFIX}{constants.SWAGGER_DOC_URL}"
        if containers.config.documentation_enabled()
        else None,
        description=constants.DESCRIPTION,
        openapi_url=f"{constants.V1_API_PREFIX}/openapi.json" if containers.config.documentation_enabled() else None,
    )
    fastapi_app.include_router(api.endpoints.router)

    return fastapi_post_initialization(fastapi_app, containers)


def create_agent_fastapi() -> FastAPI:
    settings = Settings()
    containers: Containers = init_containers(settings)
    base_service_init(containers)

    fastapi_app = FastAPI(
        title=f"{constants.PROJECT_NAME} - Agent",
        version=containers.config.version(),
        docs_url=f"{constants.V1_API_PREFIX}{constants.SWAGGER_DOC_URL}"
        if containers.config.documentation_enabled()
        else None,
        description=constants.DESCRIPTION,
        openapi_url=f"{constants.V1_API_PREFIX}/openapi.json" if containers.config.documentation_enabled() else None,
    )

    fastapi_app.include_router(api.sse.router)
    try:
        agent_url = f"{settings.genai_query_agent_settings.url}{constants.AGENT_STREAM_PREFIX}"
        containers.agent_service().register_agent(
            agent_url=agent_url, agent_timeout=settings.genai_query_agent_settings.timeout
        )

        _logger.info("Agent registration completed successfully")

    except Exception as e:
        _logger.error(
            "Failed to register agent during startup: %s. "
            "Agent functionality may be limited until registration succeeds.",
            str(e),
            exc_info=True,
        )
        raise

    return fastapi_post_initialization(fastapi_app, containers)
