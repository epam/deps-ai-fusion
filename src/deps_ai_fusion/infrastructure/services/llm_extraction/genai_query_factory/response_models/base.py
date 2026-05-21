from pydantic import BaseModel, ConfigDict

__all__ = ["ConfiguredBaseResponseModel"]


class ConfiguredBaseResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
