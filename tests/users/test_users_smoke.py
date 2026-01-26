import pytest

from api_framework.clients.users_client import UsersClient


@pytest.mark.regression
def test_get_single_user(api):
    data = UsersClient(api).get_user(1)
    assert data["id"] == 1
