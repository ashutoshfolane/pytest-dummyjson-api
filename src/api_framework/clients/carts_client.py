from __future__ import annotations

from typing import Any

import httpx

from api_framework.client import ApiClient


class CartsClient:
    def __init__(self, api: ApiClient):
        self.api = api

    # -----------------------
    # Happy path (returns JSON)
    # -----------------------

    def list_carts(self, *, limit: int = 30, skip: int = 0) -> dict[str, Any]:
        r = self.list_carts_raw(limit=limit, skip=skip)
        r.raise_for_status()
        return r.json()

    def get_cart(self, cart_id: int) -> dict[str, Any]:
        r = self.get_cart_raw(cart_id)
        r.raise_for_status()
        return r.json()

    def carts_by_user(self, user_id: int) -> dict[str, Any]:
        r = self.carts_by_user_raw(user_id)
        r.raise_for_status()
        return r.json()

    def add_cart(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.add_cart_raw(payload)
        r.raise_for_status()
        return r.json()

    def update_cart(self, cart_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.update_cart_raw(cart_id, payload)
        r.raise_for_status()
        return r.json()

    def delete_cart(self, cart_id: int) -> dict[str, Any]:
        r = self.delete_cart_raw(cart_id)
        r.raise_for_status()
        return r.json()

    # -----------------------
    # Raw helpers (status code tests)
    # -----------------------

    def list_carts_raw(self, *, limit: int = 30, skip: int = 0) -> httpx.Response:
        return self.api.get("/carts", params={"limit": limit, "skip": skip})

    def get_cart_raw(self, cart_id: int) -> httpx.Response:
        return self.api.get(f"/carts/{cart_id}")

    def carts_by_user_raw(self, user_id: int) -> httpx.Response:
        return self.api.get(f"/carts/user/{user_id}")

    def add_cart_raw(self, payload: dict[str, Any]) -> httpx.Response:
        return self.api.post("/carts/add", json=payload)

    def update_cart_raw(self, cart_id: int, payload: dict[str, Any]) -> httpx.Response:
        return self.api.request("PUT", f"/carts/{cart_id}", json=payload)

    def delete_cart_raw(self, cart_id: int) -> httpx.Response:
        return self.api.request("DELETE", f"/carts/{cart_id}")
