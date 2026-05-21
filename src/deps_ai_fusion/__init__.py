import logging

from deps_ai_fusion.settings import Settings

logging.basicConfig(
    level=Settings().logger_level.upper(),
    format="[%(asctime)s] [%(name)s: %(levelname)s] %(message)s",  # noqa: WPS323
    datefmt="%Y-%m-%d %I:%M:%S",  # noqa: WPS323
)
