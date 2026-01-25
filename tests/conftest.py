import pytest
from api_framework.config import Settings
from api_framework.client import ApiClient


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def api(settings: Settings) -> ApiClient:
    client = ApiClient(settings)
    yield client
    client.close()