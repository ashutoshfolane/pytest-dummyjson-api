from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="env/.env.local",
        extra="ignore",
    )

    base_url: HttpUrl = Field(default="https://dummyjson.com")
    timeout_seconds: float = Field(default=10.0)

    auth_header_name: str = Field(default="Authorization")
    auth_header_value: str | None = Field(default=None)