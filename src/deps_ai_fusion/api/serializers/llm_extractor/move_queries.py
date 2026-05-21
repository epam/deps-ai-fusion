from pydantic import Field

from ..base import ConfiguredBaseModel

__all__ = ["MoveQueriesRequest"]


class MoveQueriesRequest(ConfiguredBaseModel):
    source_extractor_id: str = Field(..., alias="sourceExtractorId")
    target_extractor_id: str = Field(..., alias="targetExtractorId")
    fields_codes: list[str] = Field(..., alias="fieldsCodes", min_length=1)
