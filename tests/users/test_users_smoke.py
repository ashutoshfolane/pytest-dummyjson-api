import pytest

from api_framework.clients.users_client import UsersClient


@pytest.mark.smoke
def test_list_users(api):
    data = UsersClient(api).list_users(limit=10, skip=10)

    assert "users" in data
    assert isinstance(data["users"], list)
    assert len(data["users"]) > 0
