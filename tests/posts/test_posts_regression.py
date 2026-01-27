import pytest

from api_framework.clients.posts_client import PostsClient

# -----------------------
# POSITIVE (regression)
# -----------------------


@pytest.mark.regression
def test_get_single_post(api):
    data = PostsClient(api).get_post(1)
    assert data["id"] == 1
    assert "title" in data
    assert "body" in data


@pytest.mark.regression
def test_search_posts_returns_list(api):
    data = PostsClient(api).search_posts(q="love")
    assert isinstance(data.get("posts"), list)
    assert data["total"] >= 0


@pytest.mark.regression
def test_list_posts_pagination(api):
    client = PostsClient(api)

    page1 = client.list_posts(limit=5, skip=0)
    page2 = client.list_posts(limit=5, skip=5)

    assert page1["posts"][0]["id"] != page2["posts"][0]["id"]


# -----------------------
# NEGATIVE (regression)
# -----------------------


@pytest.mark.regression
@pytest.mark.negative
def test_get_post_invalid_id_returns_404(api):
    # 0 is typically invalid in DummyJSON
    r = api.get("/posts/0")
    assert r.status_code == 404


@pytest.mark.regression
@pytest.mark.negative
def test_search_posts_empty_query_returns_200(api):
    # Not always an error; validate behavior + response shape.
    r = api.get("/posts/search", params={"q": ""})
    assert r.status_code == 200
    body = r.json()
    assert "posts" in body
    assert isinstance(body["posts"], list)
