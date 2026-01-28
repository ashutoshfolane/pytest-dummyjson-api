from __future__ import annotations

from typing import Any

from api_framework.client import ApiClient


class RecipesClient:
    def __init__(self, api: ApiClient):
        self.api = api

    def list_recipes(self, *, limit: int = 30, skip: int = 0) -> dict[str, Any]:
        r = self.api.get("/recipes", params={"limit": limit, "skip": skip})
        r.raise_for_status()
        return r.json()

    def get_recipe(self, recipe_id: int) -> dict[str, Any]:
        r = self.api.get(f"/recipes/{recipe_id}")
        r.raise_for_status()
        return r.json()

    def search_recipes(self, *, q: str) -> dict[str, Any]:
        r = self.api.get("/recipes/search", params={"q": q})
        r.raise_for_status()
        return r.json()

    def sort_recipes(self, *, sort_by: str = "name", order: str = "asc") -> dict[str, Any]:
        # DummyJSON supports sortBy/order query params on list endpoints
        r = self.api.get("/recipes", params={"sortBy": sort_by, "order": order})
        r.raise_for_status()
        return r.json()

    def list_tags(self) -> list[Any]:
        r = self.api.get("/recipes/tags")
        r.raise_for_status()
        return r.json()

    def recipes_by_tag(self, tag: str) -> dict[str, Any]:
        r = self.api.get(f"/recipes/tag/{tag}")
        r.raise_for_status()
        return r.json()

    def recipes_by_meal_type(self, meal_type: str) -> dict[str, Any]:
        r = self.api.get(f"/recipes/meal-type/{meal_type}")
        r.raise_for_status()
        return r.json()

    def add_recipe(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.post("/recipes/add", json=payload)
        r.raise_for_status()
        return r.json()

    def update_recipe(self, recipe_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.request("PUT", f"/recipes/{recipe_id}", json=payload)
        r.raise_for_status()
        return r.json()

    def delete_recipe(self, recipe_id: int) -> dict[str, Any]:
        r = self.api.request("DELETE", f"/recipes/{recipe_id}")
        r.raise_for_status()
        return r.json()
