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

    Strategy (CONSISTENCY-FIRST):
    - If username/password exist -> login and cache token in memory (preferred; avoids expired static tokens)
    - Else if AUTH_HEADER_VALUE exists -> use it (fallback path)
    """

    def __init__(self, settings: Settings, http: httpx.Client):
        self.settings = settings
        self.http = http
        self._token: str | None = None

    def _normalize_token_value(self, v: str) -> str | None:
        v = v.strip()
        if not v:
            return None
        # Allow either "Bearer <token>" OR raw token.
        if v.lower().startswith("bearer "):
            return v.split(" ", 1)[1].strip()
        return v

    def get_token(self) -> str | None:
        # Prefer minting a fresh token when creds exist (prevents "Token Expired!" flakes)
        if self._token:
            return self._token

        if self.settings.auth_username and self.settings.auth_password:
            resp = self.http.post(
                "/auth/login",
                json={
                    "username": self.settings.auth_username,
                    "password": self.settings.auth_password,
                    # optionally: "expiresInMins": 60,
                },
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            token = data.get("accessToken") or data.get("token")
            if not token:
                raise RuntimeError("Login succeeded but token not found in response")
            self._token = token
            return token

        # Fallback: token provided directly in config/env file (fast CI/local path)
        if self.settings.auth_header_value:
            return self._normalize_token_value(self.settings.auth_header_value)

        return None
