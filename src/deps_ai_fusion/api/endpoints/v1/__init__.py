from fastapi import APIRouter

from deps_ai_fusion.constants import V1_PREFIX

from .analysis import analysis_router
from .conversation import conversation_router
from .llm_coordinates import llm_coordinates_router
from .llm_extractor import llm_extractor_router

__all__ = ["router"]


router = APIRouter(prefix=V1_PREFIX)
router.include_router(conversation_router)
router.include_router(analysis_router)
router.include_router(llm_extractor_router)
router.include_router(llm_coordinates_router)
