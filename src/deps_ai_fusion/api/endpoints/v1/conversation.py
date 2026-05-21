from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Path, Query, status

from deps_ai_fusion.application import ConversationService
from deps_ai_fusion.containers import Containers

from ...auth import get_current_user_id, get_current_user_tenant
from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers.conversation import (
    CreateCompletionRequest,
    SerializedCompletion,
    SerializedConversationInfo,
)

__all__ = ["conversation_router"]

conversation_router = APIRouter(prefix="/conversations", route_class=MarkerRoute, tags=["Conversation"])


@conversation_router.get(
    "/{entityId}",
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_conversation(
    entity_id: str = Path(..., alias="entityId"),
    user_id: str = Depends(get_current_user_id),
    tenant_id: str = Depends(get_current_user_tenant),
    conversation_service: ConversationService = Depends(Provide[Containers.conversation_service]),
) -> SerializedConversationInfo:
    return SerializedConversationInfo.from_dto(
        conversation_service.get_conversation(entity_id=entity_id, user_id=user_id, tenant_id=tenant_id),
    )


@conversation_router.put(
    "/{entityId}",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_completion(
    entity_id: str = Path(..., alias="entityId"),
    user_id: str = Depends(get_current_user_id),
    tenant_id: str = Depends(get_current_user_tenant),
    completion: CreateCompletionRequest = Body(...),
    conversation_service: ConversationService = Depends(Provide[Containers.conversation_service]),
) -> SerializedCompletion:
    return SerializedCompletion.from_domain(
        conversation_service.chat_request(
            entity_id=entity_id,
            user_id=user_id,
            tenant_id=tenant_id,
            question=completion.question,
            provider=completion.provider,
            model=completion.model,
            page_span=completion.page_span.to_dict() if completion.page_span else None,  # type: ignore
            files=completion.files,
        ),
    )


@conversation_router.delete(
    "/{entityId}/completions",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def remove_completion(
    entity_id: str = Path(..., alias="entityId"),
    user_id: str = Depends(get_current_user_id),
    tenant_id: str = Depends(get_current_user_tenant),
    completion_codes: list[str] = Query(..., alias="completionCodes"),
    conversation_service: ConversationService = Depends(Provide[Containers.conversation_service]),
) -> None:
    conversation_service.remove_completions(
        entity_id=entity_id,
        user_id=user_id,
        tenant_id=tenant_id,
        completion_codes=completion_codes,
    )


@conversation_router.delete(
    "/{entityId}",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def clear_conversation(
    entity_id: str = Path(..., alias="entityId"),
    user_id: str = Depends(get_current_user_id),
    tenant_id: str = Depends(get_current_user_tenant),
    conversation_service: ConversationService = Depends(Provide[Containers.conversation_service]),
) -> None:
    conversation_service.clear_conversation(entity_id=entity_id, user_id=user_id, tenant_id=tenant_id)
