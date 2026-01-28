import pytest

from api_framework.clients.users_client import UsersClient

# -----------------------
# POSITIVE (regression)
# -----------------------


@pytest.mark.regression
def test_search_users_returns_list(api):
    data = UsersClient(api).search_users(q="emily")

    assert isinstance(data.get("users"), list)
    assert data.get("total", 0) >= 0


@pytest.mark.regression
def test_list_users_pagination(api):
    client = UsersClient(api)

    page1 = client.list_users(limit=5, skip=0)
    page2 = client.list_users(limit=5, skip=5)

    assert page1["users"][0]["id"] != page2["users"][0]["id"]


@pytest.mark.regression
def test_filter_users_by_key_value(api):
    # Use something stable. DummyJSON commonly supports filtering by "address.city" or "gender".
    data = UsersClient(api).filter_users(key="gender", value="female")
    assert isinstance(data.get("users"), list)


@pytest.mark.regression
def test_user_child_resources(api):
    client = UsersClient(api)
    user_id = 1

    carts = client.user_carts(user_id)
    posts = client.user_posts(user_id)
    todos = client.user_todos(user_id)

    assert isinstance(carts.get("carts"), list)
    assert isinstance(posts.get("posts"), list)
    assert isinstance(todos.get("todos"), list)


# -----------------------
# NEGATIVE (regression)
# -----------------------


@pytest.mark.regression
@pytest.mark.negative
def test_get_user_invalid_id_returns_404(api):
    r = UsersClient(api).get_user_raw(0)
    assert r.status_code == 404


@pytest.mark.regression
@pytest.mark.negative
def test_search_users_empty_query_returns_200(api):
    r = UsersClient(api).search_users_raw(q="")
    assert r.status_code == 200
    body = r.json()
    assert "users" in body
    assert isinstance(body["users"], list)


@pytest.mark.regression
@pytest.mark.negative
def test_filter_users_invalid_key_returns_error_or_empty(api):
    r = UsersClient(api).filter_users_raw(
        key="this.key.does.not.exist",
        value="x",
    )

    # Some public APIs return 400/404, others return empty set (200).
    if r.status_code in (400, 404):
        return

    assert r.status_code == 200
    body = r.json()
    assert "users" in body
    assert isinstance(body["users"], list)
