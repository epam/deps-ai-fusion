from fastapi import APIRouter

from deps_ai_fusion.constants import V1_API_PREFIX

from .agent import agent_router

__all__ = ["router"]

router = APIRouter(prefix=V1_API_PREFIX)

router.include_router(agent_router)
