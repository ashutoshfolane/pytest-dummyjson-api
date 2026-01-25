from __future__ import annotations

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .auth import AuthClient
from .config import Settings


class ApiClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.http = httpx.Client(
            base_url=str(settings.base_url),
            headers={"Content-Type": "application/json"},
            timeout=settings.timeout_seconds,
        )
        self.auth = AuthClient(settings, self.http)

    def close(self) -> None:
        self.http.close()

    def _auth_headers(self) -> dict[str, str]:
        token = self.auth.get_token()
        if not token:
            return {}

        header_name = (self.settings.auth_header_name or "Authorization").strip()
        # Always send Bearer <token> for DummyJSON; token is raw at this point.
        return {header_name: f"Bearer {token}"}

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
    )
    def request(self, method: str, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        headers = dict(kwargs.pop("headers", {}) or {})
        if auth:
            headers.update(self._auth_headers())

        return self.http.request(method, path, headers=headers, **kwargs)

    def get(self, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        return self.request("GET", path, auth=auth, **kwargs)

    def post(self, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        return self.request("POST", path, auth=auth, **kwargs)
