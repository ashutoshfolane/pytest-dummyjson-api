import os

import pytest

from api_framework.clients.auth_client import AuthClient


@pytest.mark.smoke
@pytest.mark.auth
def test_login_gets_token_if_creds_present(api):
    username = os.getenv("AUTH_USERNAME")
    password = os.getenv("AUTH_PASSWORD")
    if not username or not password:
        pytest.skip("Auth not configured (set AUTH_USERNAME/AUTH_PASSWORD)")

    data = AuthClient(api).login(username=username, password=password)

    # DummyJSON typically returns accessToken (and possibly refreshToken)
    assert "accessToken" in data
    assert isinstance(data["accessToken"], str)
    assert len(data["accessToken"]) > 10
