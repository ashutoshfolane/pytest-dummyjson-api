from __future__ import annotations

from typing import Any

import httpx

from api_framework.client import ApiClient


class CommentsClient:
    def __init__(self, api: ApiClient):
        self.api = api

    # -----------------------
    # READ
    # -----------------------
    def list_comments(self, *, limit: int = 30, skip: int = 0) -> dict[str, Any]:
        r = self.api.get("/comments", params={"limit": limit, "skip": skip})
        r.raise_for_status()
        return r.json()

    def get_comment(self, comment_id: int) -> dict[str, Any]:
        r = self.api.get(f"/comments/{comment_id}")
        r.raise_for_status()
        return r.json()

    def comments_by_post(self, post_id: int) -> dict[str, Any]:
        r = self.api.get(f"/comments/post/{post_id}")
        r.raise_for_status()
        return r.json()

    # -----------------------
    # WRITE (DummyJSON is "mocked" but returns shapes)
    # -----------------------
    def add_comment(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.post("/comments/add", json=payload)
        r.raise_for_status()
        return r.json()

    def update_comment(self, comment_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.request("PUT", f"/comments/{comment_id}", json=payload)
        r.raise_for_status()
        return r.json()

    def delete_comment(self, comment_id: int) -> dict[str, Any]:
        r = self.api.request("DELETE", f"/comments/{comment_id}")
        r.raise_for_status()
        return r.json()

    # -----------------------
    # RAW helpers for negative tests (no raise_for_status)
    # -----------------------
    def get_comment_raw(self, comment_id: int) -> httpx.Response:
        return self.api.get(f"/comments/{comment_id}")

    def comments_by_post_raw(self, post_id: int) -> httpx.Response:
        return self.api.get(f"/comments/post/{post_id}")
