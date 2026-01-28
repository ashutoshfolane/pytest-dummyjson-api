import pytest

from api_framework.clients.users_client import UsersClient
from api_framework.validation.schema import validate_json_schema


@pytest.mark.contract
def test_users_list_matches_schema(api):
    data = UsersClient(api).list_users(limit=10, skip=0)
    validate_json_schema(
        data,
        schema_path="tests/users/schemas/users_list.schema.json",
    )
