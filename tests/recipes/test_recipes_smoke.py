import pytest

from api_framework.clients.recipes_client import RecipesClient


@pytest.mark.smoke
def test_list_recipes_smoke(api):
    data = RecipesClient(api).list_recipes(limit=10, skip=0)

    assert isinstance(data.get("recipes"), list)
    assert data.get("limit") == 10
    assert data.get("skip") == 0


@pytest.mark.smoke
def test_get_single_recipe_smoke(api):
    data = RecipesClient(api).get_recipe(1)
    assert data["id"] == 1
    assert "name" in data


@pytest.mark.smoke
def test_add_recipe_smoke(api):
    client = RecipesClient(api)

    payload = {
        "name": "Smoke Recipe",
        "ingredients": ["Salt", "Pepper"],
        "instructions": ["Mix", "Cook"],
        "prepTimeMinutes": 10,
        "cookTimeMinutes": 10,
        "servings": 2,
        "difficulty": "Easy",
        "cuisine": "Test",
        "caloriesPerServing": 100,
        "tags": ["smoke"],
        "userId": 1,
    }

    data = client.add_recipe(payload)

    assert "id" in data
    assert data.get("name") == payload["name"]
    assert data.get("userId") == payload["userId"]


@pytest.mark.smoke
def test_update_recipe_smoke(api):
    client = RecipesClient(api)

    # Use a stable existing id for reliability (demo API updates are usually simulated)
    recipe_id = 1
    payload = {"name": "Updated Recipe Name (smoke)"}

    data = client.update_recipe(recipe_id, payload)

    assert data.get("id") == recipe_id
    assert data.get("name") == payload["name"]


@pytest.mark.smoke
def test_delete_recipe_smoke(api):
    client = RecipesClient(api)

    recipe_id = 1
    data = client.delete_recipe(recipe_id)

    assert data.get("id") == recipe_id
    assert data.get("isDeleted") is True or "isDeleted" in data
