from __future__ import annotations

from typing import Any

from api_framework.client import ApiClient


class UsersClient:
    def __init__(self, api: ApiClient):
        self.api = api

    def list_users(self, *, limit: int = 30, skip: int = 0) -> dict[str, Any]:
        r = self.api.get("/users", params={"limit": limit, "skip": skip})
        r.raise_for_status()
        return r.json()

    def get_user(self, user_id: int) -> dict[str, Any]:
        r = self.api.get(f"/users/{user_id}")
        r.raise_for_status()
        return r.json()

    def search_users(self, *, q: str) -> dict[str, Any]:
        r = self.api.get("/users/search", params={"q": q})
        r.raise_for_status()
        return r.json()

    def filter_users(self, *, key: str, value: str) -> dict[str, Any]:
        # DummyJSON supports: /users/filter?key=...&value=...
        r = self.api.get("/users/filter", params={"key": key, "value": value})
        r.raise_for_status()
        return r.json()

    def sort_users(self, *, sort_by: str = "firstName", order: str = "asc") -> dict[str, Any]:
        # DummyJSON supports sortBy/order on list endpoints
        r = self.api.get("/users", params={"sortBy": sort_by, "order": order})
        r.raise_for_status()
        return r.json()

    def user_carts(self, user_id: int) -> dict[str, Any]:
        r = self.api.get(f"/users/{user_id}/carts")
        r.raise_for_status()
        return r.json()

    def user_posts(self, user_id: int) -> dict[str, Any]:
        r = self.api.get(f"/users/{user_id}/posts")
        r.raise_for_status()
        return r.json()

    def user_todos(self, user_id: int) -> dict[str, Any]:
        r = self.api.get(f"/users/{user_id}/todos")
        r.raise_for_status()
        return r.json()

    def add_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.post("/users/add", json=payload)
        r.raise_for_status()
        return r.json()

    def update_user(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.request("PUT", f"/users/{user_id}", json=payload)
        r.raise_for_status()
        return r.json()

    def delete_user(self, user_id: int) -> dict[str, Any]:
        r = self.api.request("DELETE", f"/users/{user_id}")
        r.raise_for_status()
        return r.json()
