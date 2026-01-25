import pytest

pytestmark = pytest.mark.regression


def test_get_single_user(api):
    r = api.get("/users/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1