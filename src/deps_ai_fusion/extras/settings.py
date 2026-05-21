from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from .datasource import DBDialect, DBDriver

__all__ = ["SSLSettings", "DatabaseSettings", "ServiceInfoSettings", "SentrySettings"]


class SSLSettings(BaseSettings):
    key: str = ""
    cert: str = ""
    rootcert: str = ""
    mode: str = "verify-full"

    model_config = SettingsConfigDict(env_prefix="DATABASE_SSL_", case_sensitive=False)


class DatabaseSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: str
    db: str
    ssl: SSLSettings = SSLSettings()
    dialect: DBDialect = DBDialect.POSTGRES
    driver: DBDriver = DBDriver.PSYCOPG2
    require_secure_transport: bool = False

    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False)


class ServiceInfoSettings(BaseSettings):
    tag: str = ""
    date: str = ""
    hash: str = ""

    model_config = SettingsConfigDict(env_prefix="SERVICE_INFO_", case_sensitive=False)


class SentrySettings(BaseSettings):
    enabled: bool = False
    trace_enabled: bool = False
    dsn: Optional[str] = None
    traces_sample_rate: Optional[float] = 0

    model_config = SettingsConfigDict(env_prefix="SENTRY_", case_sensitive=False, frozen=True)
