import pytest

from api_framework.clients.auth_client import AuthApiClient
from api_framework.validation.schema import validate_json_schema

pytestmark = [pytest.mark.contract, pytest.mark.auth]


@pytest.mark.contract
@pytest.mark.auth
def test_login_contract(api, settings):
    if not (settings.auth_username and settings.auth_password):
        pytest.skip("Auth not configured")

    data = AuthApiClient(api).login(
        username=settings.auth_username, password=settings.auth_password
    )
    validate_json_schema(data, schema_path="tests/auth/schemas/auth_login.schema.json")


@pytest.mark.contract
@pytest.mark.auth
def test_me_contract(api, settings):
    if not (settings.auth_username and settings.auth_password) and not settings.auth_header_value:
        pytest.skip("Auth not configured")

    data = AuthApiClient(api).me()
    validate_json_schema(data, schema_path="tests/auth/schemas/auth_me.schema.json")


@pytest.mark.contract
@pytest.mark.auth
def test_refresh_contract(api, settings):
    if not (settings.auth_username and settings.auth_password):
        pytest.skip("Auth not configured")

    login = AuthApiClient(api).login(
        username=settings.auth_username, password=settings.auth_password
    )
    refresh_token = login.get("refreshToken")
    if not refresh_token:
        pytest.skip("refreshToken not present")

    data = AuthApiClient(api).refresh(refresh_token=refresh_token)
    validate_json_schema(data, schema_path="tests/auth/schemas/auth_refresh.schema.json")
