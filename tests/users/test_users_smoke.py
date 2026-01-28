import pytest

from api_framework.clients.users_client import UsersClient


@pytest.mark.smoke
def test_list_users_smoke(api):
    data = UsersClient(api).list_users(limit=10, skip=0)

    assert isinstance(data.get("users"), list)
    assert data.get("limit") == 10
    assert data.get("skip") == 0


@pytest.mark.smoke
def test_get_single_user_smoke(api):
    data = UsersClient(api).get_user(1)
    assert data["id"] == 1
    assert "username" in data


@pytest.mark.smoke
def test_add_user_smoke(api):
    client = UsersClient(api)

    payload = {
        "firstName": "Smoke",
        "lastName": "User",
        "age": 30,
        "username": "smoke-user",
        "password": "pass123",  # pragma: allowlist secret
    }

    data = client.add_user(payload)

    assert "id" in data
    assert data.get("firstName") == payload["firstName"]
    assert data.get("username") == payload["username"]


@pytest.mark.smoke
def test_update_user_smoke(api):
    client = UsersClient(api)

    user_id = 1
    payload = {"firstName": "UpdatedFirstName(smoke)"}

    data = client.update_user(user_id, payload)

    assert data.get("id") == user_id
    assert data.get("firstName") == payload["firstName"]


@pytest.mark.smoke
def test_delete_user_smoke(api):
    client = UsersClient(api)

    user_id = 1
    data = client.delete_user(user_id)

    assert data.get("id") == user_id
    assert data.get("isDeleted") is True or "isDeleted" in data
