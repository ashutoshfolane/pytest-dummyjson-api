from __future__ import annotations

from pathlib import Path

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="env/.env.local",
        extra="ignore",
    )

    base_url: HttpUrl = Field(default="https://dummyjson.com", validation_alias="BASE_URL")
    timeout_seconds: float = Field(default=10.0, validation_alias="TIMEOUT_SECONDS")

    retry_attempts: int = Field(default=3, validation_alias="RETRY_ATTEMPTS")

    auth_header_name: str = Field(default="Authorization", validation_alias="AUTH_HEADER_NAME")
    auth_header_value: str | None = Field(default=None, validation_alias="AUTH_HEADER_VALUE")
    auth_username: str | None = Field(default=None, validation_alias="AUTH_USERNAME")
    auth_password: str | None = Field(default=None, validation_alias="AUTH_PASSWORD")


def settings_for(env_name: str | None) -> Settings:
    env_name = (env_name or "local").strip().lower()
    candidate = Path("env") / f".env.{env_name}"
    env_file = candidate if candidate.exists() else Path("env") / ".env.local"
    return Settings(_env_file=str(env_file))
