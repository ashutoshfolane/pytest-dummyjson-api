import pytest

from api_framework.clients.comments_client import CommentsClient
from api_framework.validation.schema import validate_json_schema


@pytest.mark.contract
def test_comments_list_matches_schema(api):
    data = CommentsClient(api).list_comments(limit=10, skip=0)
    validate_json_schema(
        data,
        schema_path="tests/comments/schemas/comments_list.schema.json",
    )
