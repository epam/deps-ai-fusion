from fastapi import APIRouter, status

from deps_ai_fusion.api.endpoint_marker import MarkerRoute
from deps_ai_fusion.api.endpoint_visibility import Visibility

__all__ = ["debug_router"]

debug_router = APIRouter(prefix="/debug", tags=["Debug"], route_class=MarkerRoute)


@debug_router.get(
    "/500",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
def raise_internal_server_error():
    raise ValueError
