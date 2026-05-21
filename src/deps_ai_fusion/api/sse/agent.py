from http import HTTPStatus
from typing import Annotated, Iterator

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from sse_starlette import EventSourceResponse

from deps_ai_fusion.application import AgentService
from deps_ai_fusion.containers import Containers

from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility
from ..serializers.agent import AgentChunkResponse, AgentRequest

__all__ = ["agent_router"]

agent_router = APIRouter(prefix="/agent/stream", tags=["Agent"], route_class=MarkerRoute)


def _parse_agent_request(raw: str = Query(..., alias="request")) -> AgentRequest:
    return AgentRequest.model_validate_json(raw)


def _event_stream_sync(app: AgentService, request: AgentRequest) -> Iterator[str]:
    for chunk in app.stream_agent_response(
        conversation_id=request.conversation_id,
        turn_id=request.turn_id,
        user_question=request.user_question,
        context_bundle=request.raw_context_bundle(),
        arguments=request.raw_arguments(),
    ):
        yield AgentChunkResponse.json_from_chunk(chunk)


@agent_router.get(
    "",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": AgentChunkResponse.model_json_schema(),
                },
            },
        },
    },
)
@inject
def subscribe_to_events(
    request: Annotated[AgentRequest, Depends(_parse_agent_request)],
    app: AgentService = Depends(Provide[Containers.agent_service]),
) -> EventSourceResponse:
    return EventSourceResponse(_event_stream_sync(app, request))
