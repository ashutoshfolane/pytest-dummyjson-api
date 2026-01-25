from __future__ import annotations

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .config import Settings


class ApiClient:
    def __init__(self, settings: Settings):
        self.settings = settings

        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "pytest-api-framework/1.0",
        }

        if settings.auth_header_value:
            headers[settings.auth_header_name] = settings.auth_header_value

        self._client = httpx.Client(
            base_url=str(settings.base_url),
            headers=headers,
            timeout=settings.timeout_seconds,
        )

    def close(self) -> None:
        self._client.close()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
    )
    def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        return self._client.request(method, path, **kwargs)

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, json: dict | None = None, **kwargs) -> httpx.Response:
        return self.request("POST", path, json=json, **kwargs)
