from typing import Self

from deps_gen_ai.providers import ProviderCode
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from deps_ai_fusion.domain.model import (
    DEFAULT_CUSTOM_INSTRUCTION,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
)

from .description import AGENT_DESCRIPTION

__all__ = ["AgentSettings", "settings"]


class AgentSettings(BaseSettings):
    provider_id: ProviderCode = Field(ProviderCode.EPAM_DIAL, alias="AGENT_PROVIDER_ID")
    model_id: str = Field("gpt-4o", alias="AGENT_MODEL_ID")

    aws_region: str | None = Field(None, alias="AWS_REGION")
    aws_access_key_id: str | None = Field(None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(None, alias="AWS_SECRET_ACCESS_KEY")

    azure_api_endpoint: str | None = Field(None, alias="AZURE_API_ENDPOINT")
    azure_api_key: str | None = Field(None, alias="AZURE_API_KEY")
    azure_api_version: str | None = Field(None, alias="AZURE_API_VERSION")

    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")

    google_api_key: str | None = Field(None, alias="GOOGLE_API_KEY")

    dial_api_endpoint: str | None = Field(None, alias="EPAM_DIAL_ENDPOINT")
    dial_api_key: str | None = Field(None, alias="EPAM_DIAL_API_KEY")
    dial_api_version: str | None = Field(None, alias="EPAM_DIAL_API_VERSION")

    default_extractor_provider: ProviderCode = Field(ProviderCode.EPAM_DIAL, alias="DEFAULT_EXTRACTOR_PROVIDER")
    default_extractor_model: str = Field("openai.gpt-4-omni-text", alias="DEFAULT_EXTRACTOR_MODEL")
    default_extractor_grouping_factor: int = Field(1, alias="DEFAULT_EXTRACTOR_GROUPING_FACTOR")
    default_extractor_temperature: float = Field(DEFAULT_TEMPERATURE, alias="DEFAULT_EXTRACTOR_TEMPERATURE")
    default_extractor_top_p: float = Field(DEFAULT_TOP_P, alias="DEFAULT_EXTRACTOR_TOP_P")
    default_extractor_custom_instruction: str = Field(
        DEFAULT_CUSTOM_INSTRUCTION, alias="DEFAULT_EXTRACTOR_CUSTOM_INSTRUCTION"
    )

    agent_description: str = Field(AGENT_DESCRIPTION, alias="AGENT_DESCRIPTION")

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        provider_required_fields = {
            ProviderCode.EPAM_DIAL: (
                (self.dial_api_endpoint, self.dial_api_key, self.dial_api_version),
                "For provider 'EPAM_DIAL', please set all of: dial_api_endpoint, dial_api_key, and dial_api_version.",
            ),
            ProviderCode.AZURE: (
                (self.azure_api_endpoint, self.azure_api_key, self.azure_api_version),
                "For provider 'AZURE', please set all of: azure_api_endpoint, azure_api_key, and azure_api_version.",
            ),
            ProviderCode.OPENAI: ((self.openai_api_key,), "For provider 'OPENAI', please set openai_api_key."),
            ProviderCode.GOOGLE: ((self.google_api_key,), "For provider 'GOOGLE', please set google_api_key."),
            ProviderCode.AWS_BEDROCK: (
                (self.aws_region,),
                "For provider 'AWS_BEDROCK', please set aws_region and make sure access/secret keys are either set or role is assigned.",
            ),
        }

        required_fields, error_message = provider_required_fields.get(self.provider_id, ((), None))

        if any(field is None for field in required_fields):
            raise ValueError(error_message)

        return self


settings = AgentSettings()
