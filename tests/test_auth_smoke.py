import pytest

pytestmark = pytest.mark.smoke


def test_login_gets_token_if_creds_present(api, settings):
    # If creds not configured, skip (keeps repo usable out-of-box)
    if not (settings.auth_username and settings.auth_password) and not settings.auth_header_value:
        pytest.skip("Auth not configured (set AUTH_HEADER_VALUE or AUTH_USERNAME/AUTH_PASSWORD)")

    token = api.auth.get_token()
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 10
