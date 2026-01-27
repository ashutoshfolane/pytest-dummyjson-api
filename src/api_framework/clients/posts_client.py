from __future__ import annotations

from typing import Any

from api_framework.client import ApiClient


class PostsClient:
    def __init__(self, api: ApiClient):
        self.api = api

    def list_posts(self, *, limit: int = 30, skip: int = 0) -> dict[str, Any]:
        r = self.api.get("/posts", params={"limit": limit, "skip": skip})
        r.raise_for_status()
        return r.json()

    def get_post(self, post_id: int) -> dict[str, Any]:
        r = self.api.get(f"/posts/{post_id}")
        r.raise_for_status()
        return r.json()

    def search_posts(self, *, q: str) -> dict[str, Any]:
        r = self.api.get("/posts/search", params={"q": q})
        r.raise_for_status()
        return r.json()

    def add_post(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.post("/posts/add", json=payload)
        r.raise_for_status()
        return r.json()

    def update_post(self, post_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.request("PUT", f"/posts/{post_id}", json=payload)
        r.raise_for_status()
        return r.json()

    def delete_post(self, post_id: int) -> dict[str, Any]:
        r = self.api.request("DELETE", f"/posts/{post_id}")
        r.raise_for_status()
        return r.json()
