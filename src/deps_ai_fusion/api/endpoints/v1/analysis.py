from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, status

from deps_ai_fusion.application import AnalysisService
from deps_ai_fusion.containers import Containers

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers.analysis import (
    AvailableModelsResponse,
    FileInsightsRetrivalRequest,
    PerformDocumentInsightsRetrivalRequest,
    SerializedRetrievedInsights,
)

__all__ = ["analysis_router"]

analysis_router = APIRouter(prefix="/analysis", route_class=MarkerRoute, tags=["Analysis"])


@analysis_router.post(
    "/retrieve-insights",
    response_model=SerializedRetrievedInsights,
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def retrieve_insights(
    request: PerformDocumentInsightsRetrivalRequest = Body(...),
    service: AnalysisService = Depends(Provide[Containers.analysis_service]),
) -> SerializedRetrievedInsights:
    return SerializedRetrievedInsights.from_model(
        service.retrieve_insights(
            document_id=request.document_id,
            llm_reference=request.llm_reference,
            requested_insights=request.requested_insights_as_queries(),
            custom_instructions=request.custom_instructions,
            temperature=request.params.temperature,
            top_p=request.params.top_p,
            retrival_group_size=request.params.grouping_factor,
            page_span=request.params.page_span.to_dict() if request.params.page_span else None,  # type: ignore
            files=request.files,
        ),
    )


@analysis_router.post(
    "/retrieve-file-insights",
    response_model=SerializedRetrievedInsights,
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def retrieve_file_insights(
    request: FileInsightsRetrivalRequest = Body(...),
    service: AnalysisService = Depends(Provide[Containers.analysis_service]),
) -> SerializedRetrievedInsights:
    return SerializedRetrievedInsights.from_model(
        service.retrieve_file_insights(
            filepath=request.file_path,
            llm_reference=request.llm_reference,
            requested_insights=request.requested_insights_as_queries(),
            custom_instructions=request.custom_instructions,
            temperature=request.params.temperature,
            top_p=request.params.top_p,
            retrival_group_size=request.params.grouping_factor,
            page_span=request.params.page_span.to_dict() if request.params.page_span else None,  # type: ignore
            files=request.files,
        ),
    )


@analysis_router.get(
    "/models",
    response_model=AvailableModelsResponse,
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_available_models(
    service: AnalysisService = Depends(Provide[Containers.analysis_service]),
) -> AvailableModelsResponse:
    return AvailableModelsResponse.from_dto(service.get_available_models())
