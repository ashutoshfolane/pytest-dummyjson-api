import pytest

pytestmark = [pytest.mark.regression, pytest.mark.auth]


def test_get_me_requires_auth(api, settings):
    if not (settings.auth_username and settings.auth_password) and not settings.auth_header_value:
        pytest.skip("Auth not configured")

    r = api.get("/auth/me", auth=True)
    assert r.status_code == 200
    body = r.json()
    assert "id" in body
    assert "username" in body
