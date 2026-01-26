import pytest

from api_framework.client import ApiClient
from api_framework.config import settings_for
from api_framework.validation.settings import validate_settings


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="local",
        help="Environment name to load from env/.env.<name> (default: local)",
    )


@pytest.fixture(scope="session")
def settings(request):
    env_name = request.config.getoption("--env")
    s = settings_for(env_name)
    validate_settings(s)
    return s


@pytest.fixture(scope="session")
def api(settings):
    client = ApiClient(settings)
    yield client
    client.close()
