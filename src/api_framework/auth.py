from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .config import Settings


@dataclass
class TokenResult:
    token: str


class AuthClient:
    """
    Token auth helper.
    Strategy:
    - If AUTH_HEADER_VALUE exists -> use it (fast CI/local path)
    - Else if username/password -> login and cache token in memory
    """

    def __init__(self, settings: Settings, http: httpx.Client):
        self.settings = settings
        self.http = http
        self._token: str | None = None

    def get_token(self) -> str | None:
        # Fast path: token provided directly in config/env file
        if self.settings.auth_header_value:
            # Allow either "Bearer <token>" OR raw token.
            v = self.settings.auth_header_value.strip()
            if not v:
                return None
            if v.lower().startswith("bearer "):
                return v.split(" ", 1)[1].strip()
            return v

        if self._token:
            return self._token

        if not (self.settings.auth_username and self.settings.auth_password):
            return None

        resp = self.http.post(
            "/auth/login",
            json={
                "username": self.settings.auth_username,
                "password": self.settings.auth_password,
            },
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        token = data.get("accessToken") or data.get("token")
        if not token:
            raise RuntimeError("Login succeeded but token not found in response")
        self._token = token
        return token
