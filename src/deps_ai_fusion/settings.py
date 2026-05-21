from typing import Any

from deps_asb import ASBSettings
from deps_gen_ai.settings import ParsingServiceSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_ai_fusion.extras import DatabaseSettings, SentrySettings, ServiceInfoSettings


class FileStorageSettings(BaseSettings):
    url: str
    timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="FILE_STORAGE_", case_sensitive=False)


class ExtractionSettings(BaseSettings):
    url: str
    timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="EXTRACTION_", case_sensitive=False)


class MetaAgentSettings(BaseSettings):
    url: str
    timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="META_AGENT_", case_sensitive=False)


class AgenticAISettings(BaseSettings):
    url: str
    timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="AGENTIC_AI_", case_sensitive=False)


class GenAIQueryAgentSettings(BaseSettings):
    url: str
    timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="GENAI_QUERY_AGENT_", case_sensitive=False)


class UnifierSettings(BaseSettings):
    url: str
    timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="UNIFIER_", case_sensitive=False)


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    info: ServiceInfoSettings = ServiceInfoSettings()
    sentry: SentrySettings = SentrySettings()
    database: DatabaseSettings = DatabaseSettings()

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, validation_alias="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    documentation_enabled: bool = True
    instrumentation_enabled: bool = False
    llm_coordinates_enabled: bool = False

    extraction_settings: ExtractionSettings = ExtractionSettings()
    storage_settings: FileStorageSettings = FileStorageSettings()
    parsing_settings: ParsingServiceSettings = ParsingServiceSettings()
    meta_agent_settings: MetaAgentSettings = MetaAgentSettings()
    agentic_ai_settings: AgenticAISettings = AgenticAISettings()
    genai_query_agent_settings: GenAIQueryAgentSettings = GenAIQueryAgentSettings()
    unifier_settings: UnifierSettings = UnifierSettings()

    model_config = SettingsConfigDict(use_enum_values=True, case_sensitive=False)

    @field_validator("messaging_driver_settings")
    @classmethod
    def validate_messaging_driver_settings(cls, _: Any, info: ValidationInfo) -> Any:
        messaging_driver = info.data.get("messaging_driver")

        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()

        raise ValueError(f"Driver {driver} is not implemented")
