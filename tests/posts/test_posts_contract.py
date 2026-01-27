import pytest

from api_framework.clients.posts_client import PostsClient
from api_framework.validation.schema import validate_json_schema


@pytest.mark.contract
def test_posts_list_matches_schema(api):
    data = PostsClient(api).list_posts(limit=10, skip=0)
    validate_json_schema(
        data,
        schema_path="tests/posts/schemas/posts_list.schema.json",
    )
