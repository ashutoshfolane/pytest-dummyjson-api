import pytest
from api_framework.config import Settings
from api_framework.client import ApiClient
from api_framework.validation import validate_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    s = Settings()
    validate_settings(s)
    return s


@pytest.fixture(scope="session")
def api(settings: Settings) -> ApiClient:
    client = ApiClient(settings)
    yield client
    client.close()