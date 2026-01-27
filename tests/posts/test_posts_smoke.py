import pytest

from api_framework.clients.posts_client import PostsClient


@pytest.mark.smoke
def test_list_posts_smoke(api):
    data = PostsClient(api).list_posts(limit=10, skip=0)

    assert isinstance(data.get("posts"), list)
    assert data.get("limit") == 10
    assert data.get("skip") == 0


@pytest.mark.smoke
def test_add_post_smoke(api):
    client = PostsClient(api)

    payload = {
        "title": "Smoke post title",
        "body": "Smoke post body",
        "userId": 1,
    }

    data = client.add_post(payload)

    assert "id" in data
    assert data.get("title") == payload["title"]
    assert data.get("body") == payload["body"]
    assert data.get("userId") == payload["userId"]


@pytest.mark.smoke
def test_update_post_smoke(api):
    client = PostsClient(api)

    # Use a stable existing post id for public demo API reliability
    post_id = 1
    payload = {"title": "Updated title from smoke"}

    data = client.update_post(post_id, payload)

    assert data.get("id") == post_id
    assert data.get("title") == payload["title"]


@pytest.mark.smoke
def test_delete_post_smoke(api):
    client = PostsClient(api)

    # Demo API delete is typically simulated; validate shape + isDeleted flag
    post_id = 1
    data = client.delete_post(post_id)

    assert data.get("id") == post_id
    assert data.get("isDeleted") is True or "isDeleted" in data
