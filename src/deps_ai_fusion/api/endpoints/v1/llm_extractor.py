from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Path, status

from deps_ai_fusion.application import LLMExtractionService
from deps_ai_fusion.containers import Containers

from ...auth import get_current_user_tenant
from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import (
    AssignLLMToExtractorRequest,
    AssignLLMToExtractorResponse,
    CreateExtractorRequest,
    CreateExtractorResponse,
    GetLLMExtractorsResponse,
    MoveQueriesRequest,
    SerializedLLMWorkflow,
    SerializedQuery,
    UpdateExtractorRequest,
    UpdateExtractorResponse,
)

__all__ = ["llm_extractor_router"]

llm_extractor_router = APIRouter(prefix="", route_class=MarkerRoute, tags=["LLM Extractor"])


@llm_extractor_router.post(
    "/document-types/{documentTypeId}/llm-extractors/{extractorId}/query",
    response_model=SerializedQuery,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def add_query(
    document_type_id: str = Path(..., alias="documentTypeId"),
    extractor_id: str = Path(..., alias="extractorId"),
    query_data: SerializedQuery = Body(...),
    tenant_id: str = Depends(get_current_user_tenant),
    service: LLMExtractionService = Depends(Provide[Containers.llm_extraction_service]),
) -> SerializedQuery:

    return SerializedQuery.from_model(
        service.add_query(
            code=query_data.code,
            raw_workflow=query_data.workflow.to_dict(),
            raw_data_shape=query_data.shape.to_dict(),
            document_type_id=document_type_id,
            extractor_id=extractor_id,
            tenant_id=tenant_id,
        ),
    )


@llm_extractor_router.patch(
    "/document-types/{documentTypeId}/llm-extractors/{extractorId}/query/{code}",
    response_model=SerializedQuery,
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def update_query(
    code: str,
    workflow: SerializedLLMWorkflow = Body(..., embed=True),
    document_type_id: str = Path(..., alias="documentTypeId"),
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(get_current_user_tenant),
    service: LLMExtractionService = Depends(Provide[Containers.llm_extraction_service]),
) -> SerializedQuery:
    return SerializedQuery.from_model(
        service.update_query(
            document_type_id=document_type_id,
            extractor_id=extractor_id,
            tenant_id=tenant_id,
            code=code,
            raw_workflow=workflow.to_dict(),
        ),
    )


@llm_extractor_router.post(
    "/document-types/llm-extractors",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=CreateExtractorResponse,
)
@inject
def create_extractor(
    request: CreateExtractorRequest = Body(...),
    tenant_id: str = Depends(get_current_user_tenant),
    service: LLMExtractionService = Depends(Provide[Containers.llm_extraction_service]),
) -> CreateExtractorResponse:
    document_type_id, extractor_id = service.create_extractor(
        tenant_id=tenant_id,
        **request.to_dict(),
    )
    return CreateExtractorResponse(documentTypeId=document_type_id, extractorId=extractor_id)


@llm_extractor_router.put(
    "/document-types/{documentTypeId}/llm-extractors/{extractorId}",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=UpdateExtractorResponse,
)
@inject
def update_extractor(
    request: UpdateExtractorRequest,
    document_type_id: str = Path(..., alias="documentTypeId"),
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(get_current_user_tenant),
    service: LLMExtractionService = Depends(Provide[Containers.llm_extraction_service]),
) -> UpdateExtractorResponse:
    service.update_extractor(
        extractor_id=extractor_id,
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        name=request.name,
        custom_instruction=request.extraction_params.custom_instruction,
        grouping_factor=request.extraction_params.grouping_factor,
        temperature=request.extraction_params.temperature,
        top_p=request.extraction_params.top_p,
        page_span=request.extraction_params.page_span.to_dict() if request.extraction_params.page_span else None,
        context_attachments=request.extraction_params.context_attachments,
    )

    return UpdateExtractorResponse(extractor_id=extractor_id, document_type_id=document_type_id)


@llm_extractor_router.post(
    "/document-types/{documentTypeId}/llm-extractors/move-queries",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def move_queries_between_extractors(
    request: MoveQueriesRequest = Body(...),
    document_type_id: str = Path(..., alias="documentTypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    service: LLMExtractionService = Depends(Provide[Containers.llm_extraction_service]),
) -> None:
    service.move_queries_between_extractors(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        source_extractor_id=request.source_extractor_id,
        target_extractor_id=request.target_extractor_id,
        fields_codes=request.fields_codes,
    )


@llm_extractor_router.put(
    "/document-types/{documentTypeId}/llm-extractors/{extractorId}/llm",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=AssignLLMToExtractorResponse,
)
@inject
def assign_llm_to_extractor(
    request: AssignLLMToExtractorRequest,
    document_type_id: str = Path(..., alias="documentTypeId"),
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(get_current_user_tenant),
    service: LLMExtractionService = Depends(Provide[Containers.llm_extraction_service]),
) -> AssignLLMToExtractorResponse:
    service.assign_llm_to_extractor(
        extractor_id=extractor_id,
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        provider=request.provider,
        model=request.model,
    )

    return AssignLLMToExtractorResponse(extractor_id=extractor_id, document_type_id=document_type_id)


@llm_extractor_router.get(
    "/document-types/{documentTypeId}/llm-extractors",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=GetLLMExtractorsResponse,
)
@inject
def get_llm_extractors(
    document_type_id: str = Path(..., alias="documentTypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    service: LLMExtractionService = Depends(Provide[Containers.llm_extraction_service]),
) -> GetLLMExtractorsResponse:

    llm_extractors = service.get_llm_extractors_for_document_type(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
    )

    return GetLLMExtractorsResponse.from_list(llm_extractors)
