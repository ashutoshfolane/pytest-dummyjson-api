import pytest

pytestmark = pytest.mark.smoke


def test_list_users(api):
    r = api.get("/users", params={"limit": 10, "skip": 10})
    assert r.status_code == 200, f"Unexpected status={r.status_code}, body={r.text[:300]}"

    data = r.json()
    assert "users" in data
    assert isinstance(data["users"], list)
    assert len(data["users"]) == 10
    assert data["skip"] == 10
    assert data["limit"] == 10
