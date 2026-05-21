from pydantic import BaseModel

__all__ = ["InsightsPayload"]


class InsightsPayload(BaseModel):
    insights: list[str] = []
