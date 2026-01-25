from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_url: HttpUrl = Field(default="https://dummyjson.com")
    timeout_seconds: float = Field(default=10.0)

    # Optional. ReqRes docs mention using x-api-key for stable project-scoped responses.
    # We keep it optional so the framework works out-of-box.
    api_key: str | None = Field(default=None)

    # Optional header sometimes required per docs when environment errors happen
    reqres_env: str | None = Field(default=None)  # "prod" or "dev"
