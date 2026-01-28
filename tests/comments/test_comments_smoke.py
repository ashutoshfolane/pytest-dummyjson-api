import pytest

from api_framework.clients.comments_client import CommentsClient


@pytest.mark.smoke
def test_create_comment_smoke(api):
    client = CommentsClient(api)

    created = client.add_comment(
        {
            "body": "Nice post!",
            "postId": 1,
            "userId": 1,
        }
    )

    assert isinstance(created, dict)
    assert "id" in created
    assert created.get("body") == "Nice post!"


@pytest.mark.smoke
def test_update_comment_smoke(api):
    client = CommentsClient(api)

    # Use a stable, existing comment id for guaranteed behavior on DummyJSON
    updated = client.update_comment(1, {"body": "Updated comment"})

    assert isinstance(updated, dict)
    assert updated.get("id") == 1
    assert updated.get("body") == "Updated comment"


@pytest.mark.smoke
def test_delete_comment_smoke(api):
    client = CommentsClient(api)

    # Use a stable, existing comment id for guaranteed behavior on DummyJSON
    deleted = client.delete_comment(1)

    assert isinstance(deleted, dict)
    # DummyJSON usually returns {"id": 1, "isDeleted": true, ...}
    assert deleted.get("id") == 1
    assert deleted.get("isDeleted") is True
