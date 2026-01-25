import pytest

pytestmark = pytest.mark.smoke


def test_list_users(api):
    r = api.get("/users", params={"limit": 10, "skip": 10})
    assert r.status_code == 200
    data = r.json()
    assert "users" in data
    assert len(data["users"]) == 10
