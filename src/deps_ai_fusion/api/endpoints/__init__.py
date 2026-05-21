# type: ignore
from fastapi import APIRouter

from ...constants import BASE_API_PREFIX
from .debug import *
from .healthcheck import *
from .service_info import *
from .v1 import router as v1_router

__all__ = ["router"]


router = APIRouter(prefix=BASE_API_PREFIX)

router.include_router(v1_router)
router.include_router(debug_router)
router.include_router(healthcheck_router)
router.include_router(service_info_router)
