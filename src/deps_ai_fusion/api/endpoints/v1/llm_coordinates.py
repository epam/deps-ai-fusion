from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Path

from deps_ai_fusion.application import LLMCoordinatesService
from deps_ai_fusion.containers import Containers

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import FieldCodes

__all__ = ["llm_coordinates_router"]

llm_coordinates_router = APIRouter(prefix="/llm-coordinates", route_class=MarkerRoute, tags=["LLM Coordinates"])


@llm_coordinates_router.post(
    "/{entityId}",
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def add_llm_coordinates(
    entity_id: str = Path(..., alias="entityId"),
    field_codes: FieldCodes = Body(...),
    service: LLMCoordinatesService = Depends(Provide[Containers.llm_coordinates_service]),
) -> None:
    service.add_llm_coordinates(entity_id, field_codes.codes)
