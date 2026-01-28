from __future__ import annotations

from typing import Any

import httpx

from api_framework.client import ApiClient


class ProductsClient:
    def __init__(self, api: ApiClient):
        self.api = api

    def list_products(self, *, limit: int = 30, skip: int = 0) -> dict[str, Any]:
        r = self.api.get("/products", params={"limit": limit, "skip": skip})
        r.raise_for_status()
        return r.json()

    def get_product(self, product_id: int) -> dict[str, Any]:
        r = self.api.get(f"/products/{product_id}")
        r.raise_for_status()
        return r.json()

    def search_products(self, *, q: str) -> dict[str, Any]:
        r = self.api.get("/products/search", params={"q": q})
        r.raise_for_status()
        return r.json()

    def add_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.post("/products/add", json=payload)
        r.raise_for_status()
        return r.json()

    def update_product(self, product_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        r = self.api.request("PUT", f"/products/{product_id}", json=payload)
        r.raise_for_status()
        return r.json()

    def delete_product(self, product_id: int) -> dict[str, Any]:
        r = self.api.request("DELETE", f"/products/{product_id}")
        r.raise_for_status()
        return r.json()

    def list_categories(self) -> list[str]:
        """
        DummyJSON categories shape can vary:
        - list[str] OR
        - list[{"slug": "...", "name": "...", "url": "..."}]
        Normalize to list[str] of slugs.
        """
        r = self.api.get("/products/categories")
        r.raise_for_status()
        data = r.json()

        if not isinstance(data, list):
            raise AssertionError(f"Expected list for categories, got: {type(data)}")

        slugs: list[str] = []
        for item in data:
            if isinstance(item, str):
                slugs.append(item)
            elif isinstance(item, dict):
                slug = item.get("slug") or item.get("name")
                if isinstance(slug, str) and slug.strip():
                    slugs.append(slug.strip())
            # else ignore unknown shapes

        if not slugs:
            raise AssertionError("No category slugs found in /products/categories response")

        return slugs

    def products_by_category(self, category_slug: str) -> dict[str, Any]:
        r = self.api.get(f"/products/category/{category_slug}")
        r.raise_for_status()
        return r.json()

    # -----------------------
    # RAW helpers
    # -----------------------
    def get_product_raw(self, product_id: int) -> httpx.Response:
        return self.api.get(f"/products/{product_id}")

    def products_by_category_raw(self, category_slug: str) -> httpx.Response:
        return self.api.get(f"/products/category/{category_slug}")

    def search_products_raw(self, *, q: str) -> httpx.Response:
        return self.api.get("/products/search", params={"q": q})
