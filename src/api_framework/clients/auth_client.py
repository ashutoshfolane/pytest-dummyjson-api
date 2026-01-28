from __future__ import annotations

from typing import Any

import httpx

from api_framework.client import ApiClient


class AuthApiClient:
    """
    Domain client for DummyJSON Auth endpoints:
      - POST /auth/login
      - GET  /auth/me
      - POST /auth/refresh

    Pattern:
      - strict methods -> raise_for_status() -> use in smoke + positive tests
      - raw methods -> return Response -> use in negative tests
    """

    def __init__(self, api: ApiClient):
        self.api = api

    # -----------------------
    # STRICT methods (positive)
    # -----------------------

    def login(
        self, *, username: str, password: str, expires_in_mins: int | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"username": username, "password": password}
        if expires_in_mins is not None:
            payload["expiresInMins"] = expires_in_mins

        r = self.api.post("/auth/login", json=payload)
        r.raise_for_status()
        return r.json()

    def me(self) -> dict[str, Any]:
        r = self.api.get("/auth/me", auth=True)
        r.raise_for_status()
        return r.json()

    def refresh(self, *, refresh_token: str, expires_in_mins: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"refreshToken": refresh_token}
        if expires_in_mins is not None:
            payload["expiresInMins"] = expires_in_mins

        r = self.api.post("/auth/refresh", json=payload)
        r.raise_for_status()
        return r.json()

    # -----------------------
    # RAW methods (negative)
    # -----------------------

    def login_raw(
        self, *, username: str, password: str, expires_in_mins: int | None = None
    ) -> httpx.Response:
        payload: dict[str, Any] = {"username": username, "password": password}
        if expires_in_mins is not None:
            payload["expiresInMins"] = expires_in_mins
        return self.api.post("/auth/login", json=payload)

    def me_raw(self) -> httpx.Response:
        return self.api.get("/auth/me", auth=True)

    def me_with_token_raw(self, token_value: str) -> httpx.Response:
        # Send the token explicitly, bypassing framework auth helper.
        return self.api.get("/auth/me", headers={"Authorization": token_value})

    def refresh_raw(
        self, *, refresh_token: str, expires_in_mins: int | None = None
    ) -> httpx.Response:
        payload: dict[str, Any] = {"refreshToken": refresh_token}
        if expires_in_mins is not None:
            payload["expiresInMins"] = expires_in_mins
        return self.api.post("/auth/refresh", json=payload)
