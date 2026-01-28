import pytest

from api_framework.clients.recipes_client import RecipesClient
from api_framework.validation.schema import validate_json_schema


@pytest.mark.contract
def test_recipes_list_matches_schema(api):
    data = RecipesClient(api).list_recipes(limit=10, skip=0)
    validate_json_schema(
        data,
        schema_path="tests/recipes/schemas/recipes_list.schema.json",
    )
