import pytest

from api_framework.clients.carts_client import CartsClient
from api_framework.validation.schema import validate_json_schema


@pytest.mark.contract
def test_carts_list_matches_schema(api):
    data = CartsClient(api).list_carts(limit=10, skip=0)
    validate_json_schema(
        data,
        schema_path="tests/carts/schemas/carts_list.schema.json",
    )
