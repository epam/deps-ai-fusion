from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_ai_fusion.api.endpoint_marker import MarkerRoute
from deps_ai_fusion.api.endpoint_visibility import Visibility
from deps_ai_fusion.api.serializers.build_info import BuildInfoSerializer
from deps_ai_fusion.containers import Core

__all__ = ["service_info_router"]

service_info_router = APIRouter(prefix="/service-info", route_class=MarkerRoute)


@service_info_router.get(
    "/version",
    tags=["Service Info"],
    response_model=BuildInfoSerializer,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_build_info(build_info=Depends(Provide[Core.build_info])):
    return BuildInfoSerializer(**build_info)
