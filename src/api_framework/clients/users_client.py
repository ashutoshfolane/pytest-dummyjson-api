from __future__ import annotations

from typing import Any

from api_framework.client import ApiClient


class UsersClient:
    def __init__(self, api: ApiClient):
        self.api = api

    def list_users(self, *, limit: int = 10, skip: int = 0) -> dict[str, Any]:
        """
        GET /users?limit=&skip=
        Returns parsed JSON response (dict).
        """
        r = self.api.get("/users", params={"limit": limit, "skip": skip})
        r.raise_for_status()
        return r.json()

    def get_user(self, user_id: int) -> dict[str, Any]:
        """
        GET /users?{user_id}=
        Returns parsed JSON response (dict).
        """
        r = self.api.get(f"/users/{user_id}")
        r.raise_for_status()
        return r.json()
