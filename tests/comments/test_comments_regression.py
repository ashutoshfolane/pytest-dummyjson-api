import pytest

from api_framework.clients.comments_client import CommentsClient

# -----------------------
# POSITIVE (regression)
# -----------------------


@pytest.mark.regression
def test_list_comments_returns_list(api):
    data = CommentsClient(api).list_comments(limit=10, skip=0)

    assert isinstance(data.get("comments"), list)
    assert data["total"] >= 0


@pytest.mark.regression
def test_get_single_comment(api):
    client = CommentsClient(api)
    data = client.get_comment(comment_id=1)

    assert isinstance(data, dict)
    assert data["id"] == 1
    assert "body" in data


@pytest.mark.regression
def test_comments_pagination(api):
    client = CommentsClient(api)

    page1 = client.list_comments(limit=5, skip=0)
    page2 = client.list_comments(limit=5, skip=5)

    assert page1["comments"][0]["id"] != page2["comments"][0]["id"]


@pytest.mark.regression
def test_comments_by_post_id(api):
    client = CommentsClient(api)

    data = client.comments_by_post(post_id=1)
    assert isinstance(data.get("comments"), list)
    assert all(c.get("postId") == 1 for c in data["comments"])


# -----------------------
# NEGATIVE (regression)
# -----------------------


@pytest.mark.regression
@pytest.mark.negative
def test_get_comment_invalid_id_returns_404(api):
    client = CommentsClient(api)
    r = client.get_comment_raw(comment_id=0)

    assert r.status_code == 404


@pytest.mark.regression
@pytest.mark.negative
def test_comments_by_post_invalid_post_returns_error_or_empty(api):
    client = CommentsClient(api)
    r = client.comments_by_post_raw(post_id=0)

    # DummyJSON is inconsistent: sometimes 404/400, sometimes empty list
    if r.status_code in (400, 404):
        return

    assert r.status_code == 200
    body = r.json()
    assert "comments" in body
    assert isinstance(body["comments"], list)
    assert len(body["comments"]) == 0
