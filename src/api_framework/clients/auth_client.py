from __future__ import annotations

from typing import Any

from api_framework.client import ApiClient


class AuthClient:
    def __init__(self, api: ApiClient):
        self.api = api

    def login(
        self, *, username: str, password: str, expires_in_mins: int | None = None
    ) -> dict[str, Any]:
        """
        POST /auth/login
        Returns parsed JSON response (dict).
        """
        payload: dict[str, Any] = {"username": username, "password": password}
        if expires_in_mins is not None:
            payload["expiresInMins"] = expires_in_mins

        r = self.api.post("/auth/login", json=payload)
        r.raise_for_status()
        return r.json()

    def me(self) -> dict[str, Any]:
        """
        GET /auth/me (requires auth)
        """
        r = self.api.get("/auth/me", auth=True)
        r.raise_for_status()
        return r.json()
