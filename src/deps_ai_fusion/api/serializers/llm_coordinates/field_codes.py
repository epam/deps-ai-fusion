from pydantic import Field

from ..base import ConfiguredBaseModel

__all__ = ["FieldCodes"]


class FieldCodes(ConfiguredBaseModel):
    codes: list[str] = Field(..., alias="fieldCodes")
