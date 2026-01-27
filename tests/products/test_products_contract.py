import pytest

from api_framework.clients.products_client import ProductsClient
from api_framework.validation.schema import validate_json_schema


@pytest.mark.contract
def test_products_list_matches_schema(api):
    data = ProductsClient(api).list_products(limit=10, skip=0)
    validate_json_schema(
        data,
        schema_path="tests/products/schemas/products_list.schema.json",
    )
