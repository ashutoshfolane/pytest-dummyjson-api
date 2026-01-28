import pytest

from api_framework.clients.auth_client import AuthApiClient


@pytest.mark.smoke
@pytest.mark.auth
def test_login_returns_tokens(api, settings):
    if not (settings.auth_username and settings.auth_password):
        pytest.skip("Auth not configured (set AUTH_USERNAME/AUTH_PASSWORD)")

    data = AuthApiClient(api).login(
        username=settings.auth_username, password=settings.auth_password
    )

    # DummyJSON returns accessToken + refreshToken (may also include token in older variants)
    assert isinstance(data, dict)
    assert data.get("accessToken") or data.get("token")
    assert data.get("refreshToken")


@pytest.mark.smoke
@pytest.mark.auth
def test_me_returns_user_profile(api, settings):
    # This uses framework AuthClient token injection through api.get(..., auth=True)
    if not (settings.auth_username and settings.auth_password) and not settings.auth_header_value:
        pytest.skip("Auth not configured")

    body = AuthApiClient(api).me()
    assert "id" in body
    assert "username" in body
