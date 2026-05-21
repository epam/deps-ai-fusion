from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

__all__ = ["ConfiguredBaseModel"]


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            date: date.isoformat,
            datetime: datetime.isoformat,
        },
        from_attributes=True,
        arbitrary_types_allowed=True,
    )
