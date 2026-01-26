import pytest

from api_framework.clients.users_client import UsersClient
from api_framework.validation.schema import validate_json_schema


@pytest.mark.contract
def test_users_list_contract(api):
    body = UsersClient(api).list_users(limit=10, skip=10)
    validate_json_schema(body, "tests/schemas/users_list.schema.json")
