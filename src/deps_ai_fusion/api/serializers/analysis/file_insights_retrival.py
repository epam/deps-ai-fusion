from pydantic import Field

from .base_insights_request import BaseInsightsRequest

__all__ = ["FileInsightsRetrivalRequest"]


class FileInsightsRetrivalRequest(BaseInsightsRequest):
    file_path: str = Field(
        ...,
        alias="filePath",
        description="The path from DEPS File Storage to be recognized.",
    )
