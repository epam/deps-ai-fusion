from pydantic import Field

from .base_insights_request import BaseInsightsRequest

__all__ = ["PerformDocumentInsightsRetrivalRequest"]


class PerformDocumentInsightsRetrivalRequest(BaseInsightsRequest):
    document_id: str = Field(..., alias="documentId")
