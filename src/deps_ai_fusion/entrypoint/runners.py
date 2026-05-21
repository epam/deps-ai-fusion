import logging
import os

import uvicorn

from deps_ai_fusion.containers import Containers
from deps_ai_fusion.settings import Settings

from .initializers import base_service_init, init_containers

__all__ = ["run_api", "run_message_dispatcher", "run_agent_api"]


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def run_api():
    use_web_concurrency = "WEB_CONCURRENCY" in os.environ
    env = os.getenv("ENV", "prod")
    options = {
        "host": "0.0.0.0",  # noqa: S104
        "port": 8000,
        "log_level": os.getenv("LOG_LEVEL", "debug").lower(),
        "workers": os.getenv("WEB_CONCURRENCY") if use_web_concurrency else 3,
        "reload": env == "development",
        "debug": env == "development",
    }

    uvicorn.run("deps_ai_fusion.entrypoint.api_creators:create_fastapi", **options)


def run_message_dispatcher() -> None:
    settings = Settings()
    containers: Containers = init_containers(settings)
    base_service_init(containers)

    dispatcher = containers.message_dispatcher()
    dispatcher.start_consuming()


def run_agent_api():
    use_web_concurrency = "WEB_CONCURRENCY" in os.environ
    env = os.getenv("ENV", "prod")
    options = {
        "host": "0.0.0.0",  # noqa: S104
        "port": 8000,
        "log_level": os.getenv("LOG_LEVEL", "debug").lower(),
        "workers": os.getenv("WEB_CONCURRENCY") if use_web_concurrency else 2,
        "reload": env == "development",
        "debug": env == "development",
    }

    uvicorn.run("deps_ai_fusion.entrypoint.api_creators:create_agent_fastapi", **options)
