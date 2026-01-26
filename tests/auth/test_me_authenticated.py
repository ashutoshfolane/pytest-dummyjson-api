import pytest

from api_framework.clients.auth_client import AuthClient


@pytest.mark.regression
@pytest.mark.auth
def test_get_me_requires_auth(api, settings):
    if not (settings.auth_username and settings.auth_password) and not settings.auth_header_value:
        pytest.skip("Auth not configured")

    body = AuthClient(api).me()
    assert "id" in body
    assert "username" in body
