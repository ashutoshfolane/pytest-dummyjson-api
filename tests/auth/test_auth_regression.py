import pytest

from api_framework.clients.auth_client import AuthApiClient

# -----------------------
# POSITIVE (regression)
# -----------------------


@pytest.mark.regression
@pytest.mark.auth
def test_login_with_expires_in_mins_returns_tokens(api, settings):
    if not (settings.auth_username and settings.auth_password):
        pytest.skip("Auth not configured (set AUTH_USERNAME/AUTH_PASSWORD)")

    data = AuthApiClient(api).login(
        username=settings.auth_username,
        password=settings.auth_password,
        expires_in_mins=30,
    )
    assert data.get("accessToken") or data.get("token")
    assert data.get("refreshToken")


@pytest.mark.regression
@pytest.mark.auth
def test_refresh_token_returns_new_access_token(api, settings):
    if not (settings.auth_username and settings.auth_password):
        pytest.skip("Auth not configured (set AUTH_USERNAME/AUTH_PASSWORD)")

    login = AuthApiClient(api).login(
        username=settings.auth_username, password=settings.auth_password
    )
    refresh_token = login.get("refreshToken")
    if not refresh_token:
        pytest.skip("refreshToken not present in login response (endpoint behavior changed)")

    refreshed = AuthApiClient(api).refresh(refresh_token=refresh_token)
    assert refreshed.get("accessToken") or refreshed.get("token")


# -----------------------
# NEGATIVE (regression)
# -----------------------


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.negative
def test_login_invalid_password_returns_401_or_400(api, settings):
    if not settings.auth_username:
        pytest.skip("Auth username not configured")

    r = AuthApiClient(api).login_raw(username=settings.auth_username, password="wrong-password")
    assert r.status_code in (400, 401)


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.negative
def test_me_with_invalid_token_returns_non_200(api):
    r = AuthApiClient(api).me_with_token_raw("Bearer invalid.token.value")

    # DummyJSON sometimes returns 500 for invalid tokens (server-side bug/behavior).
    # For negative auth, what we care about is "request must NOT be treated as success".
    assert r.status_code != 200


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.negative
def test_refresh_with_invalid_token_returns_4xx(api):
    r = AuthApiClient(api).refresh_raw(refresh_token="invalid-refresh-token")
    assert r.status_code in (400, 401, 403)
