from __future__ import annotations

import json
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .auth import AuthClient
from .config import Settings
from .redaction import redact_headers, redact_json


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

    # -----------------------
    # Pretty / JSON-style logs
    # -----------------------

    @staticmethod
    def _pretty(obj: Any) -> str:
        return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True)

    def _safe_request_body(self, req: httpx.Request) -> Any | None:
        if not req.content:
            return None
        try:
            body = json.loads(req.content.decode("utf-8"))
            return redact_json(body)
        except Exception:
            return f"<non-json payload, {len(req.content)} bytes>"

    def _safe_response_body(self, resp: httpx.Response) -> Any | None:
        """
        Returns a sanitized response body that is safe to print.
        Also trims very large common payloads for readability.
        """
        try:
            ct = resp.headers.get("content-type", "")
            if ct.startswith("application/json"):
                data = redact_json(resp.json())

                # Readability: trim huge DummyJSON list payloads (e.g., /users)
                if isinstance(data, dict):
                    for key in ("users", "products", "posts", "comments", "todos"):
                        if key in data and isinstance(data[key], list) and len(data[key]) > 2:
                            data[key] = data[key][:2]
                            data["_note"] = (
                                f"{key} trimmed to first 2 items for console readability"
                            )
                            break

                return data

            # Don't dump massive HTML/text
            txt = resp.text
            return (txt[:500] + "…") if len(txt) > 500 else txt
        except Exception:
            return "<unavailable>"

    def _safe_log(self, req: httpx.Request, resp: httpx.Response | None = None) -> None:
        # Request (JSON-ish blocks)
        print("\n=== REQUEST ===")
        print(self._pretty({"method": req.method, "url": str(req.url)}))
        print(self._pretty({"headers": redact_headers(dict(req.headers))}))

        req_body = self._safe_request_body(req)
        if req_body is not None:
            print(self._pretty({"body": req_body}))

        # Response (JSON-ish blocks)
        if resp is not None:
            print("\n=== RESPONSE ===")
            print(self._pretty({"status_code": resp.status_code}))
            print(self._pretty({"headers": redact_headers(dict(resp.headers))}))
            print(self._pretty({"body": self._safe_response_body(resp)}))

    # -----------------------
    # HTTP
    # -----------------------

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

        # Build request so we can log sanitized request/response every time.
        req = self.http.build_request(method, path, headers=headers, **kwargs)

        try:
            resp = self.http.send(req)
        except Exception:
            # Network/transport error: log sanitized request (no response available)
            self._safe_log(req)
            raise

        # Always log (sanitized) – pass or fail
        self._safe_log(req, resp)

        return resp

    def get(self, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        return self.request("GET", path, auth=auth, **kwargs)

    def post(self, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        return self.request("POST", path, auth=auth, **kwargs)
