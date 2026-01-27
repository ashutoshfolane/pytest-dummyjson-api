from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any

import httpx

from .auth import AuthClient
from .config import Settings
from .redaction import redact_headers, redact_json


class ApiClient:
    def __init__(self, settings: Settings):
        self.settings = settings

        # Debug kit toggle:
        # - API_DEBUG_LOG=1 enables pretty request/response + retries/timing logs
        self.debug_log_enabled = os.getenv("API_DEBUG_LOG", "").strip() == "1"

        # Debug kit: correlation id header name
        self.correlation_header_name = "x-correlation-id"

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

    @staticmethod
    def _new_correlation_id() -> str:
        return uuid.uuid4().hex

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

    def _safe_log(
        self,
        req: httpx.Request,
        resp: httpx.Response | None = None,
        *,
        correlation_id: str | None = None,
        duration_ms: int | None = None,
        retry_attempt: int | None = None,
    ) -> None:
        if not self.debug_log_enabled:
            return

        # Request (JSON-ish blocks)
        print("\n=== REQUEST ===")
        meta: dict[str, Any] = {"method": req.method, "url": str(req.url)}
        if correlation_id:
            meta["correlation_id"] = correlation_id
        if retry_attempt is not None:
            meta["retry_attempt"] = retry_attempt
        if duration_ms is not None:
            meta["duration_ms"] = duration_ms
        print(self._pretty(meta))
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

    def _log_attempt_failed(
        self,
        *,
        correlation_id: str,
        retry_attempt: int,
        duration_ms: int,
        exc: Exception,
    ) -> None:
        if not self.debug_log_enabled:
            return

        print("\n=== ATTEMPT FAILED ===")
        print(
            self._pretty(
                {
                    "correlation_id": correlation_id,
                    "retry_attempt": retry_attempt,
                    "duration_ms": duration_ms,
                    "exception_type": type(exc).__name__,
                    "exception": str(exc),
                }
            )
        )

    def _log_retry_sleep(
        self, *, correlation_id: str, retry_attempt: int, sleep_seconds: float
    ) -> None:
        if not self.debug_log_enabled:
            return

        print("\n=== RETRY ===")
        print(
            self._pretty(
                {
                    "correlation_id": correlation_id,
                    "retry_attempt": retry_attempt,
                    "sleep_seconds": sleep_seconds,
                }
            )
        )

    def _log_give_up(self, *, correlation_id: str, attempts: int, exc: Exception) -> None:
        if not self.debug_log_enabled:
            return

        print("\n=== GIVE UP ===")
        print(
            self._pretty(
                {
                    "correlation_id": correlation_id,
                    "attempts": attempts,
                    "exception_type": type(exc).__name__,
                    "exception": str(exc),
                }
            )
        )

    # -----------------------
    # HTTP
    # -----------------------

    def request(self, method: str, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        """
        Retries + Debug kit:
        - Stable correlation id across retries for the same logical request
        - Per-attempt duration (ms)
        - Retry backoff info
        - Final GIVE UP block after last attempt
        """
        initial_headers = dict(kwargs.pop("headers", {}) or {})

        # Debug kit: correlation id on every request (stable across retries)
        correlation_id = (
            initial_headers.get(self.correlation_header_name) or self._new_correlation_id()
        )

        # Use configured attempts if present; default to 3 otherwise.
        attempts = int(getattr(self.settings, "retry_attempts", 3) or 3)

        # Backoff policy similar to what we had with tenacity:
        # 0.5, 1.0, 2.0 ... capped at 4.0 seconds
        multiplier = 0.5
        min_sleep = 0.5
        max_sleep = 4.0

        for attempt_num in range(1, attempts + 1):
            # Rebuild headers each attempt (safe + avoids mutation surprises)
            headers = dict(initial_headers)
            headers[self.correlation_header_name] = correlation_id

            if auth:
                headers.update(self._auth_headers())

            # Build request so we can log sanitized request/response every time.
            req = self.http.build_request(method, path, headers=headers, **kwargs)

            start = time.perf_counter()
            try:
                resp = self.http.send(req)
                duration_ms = int((time.perf_counter() - start) * 1000)

                # Always log (sanitized) – pass or fail
                self._safe_log(
                    req,
                    resp,
                    correlation_id=correlation_id,
                    duration_ms=duration_ms,
                    retry_attempt=attempt_num,
                )
                return resp

            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                duration_ms = int((time.perf_counter() - start) * 1000)

                # Log request block (sanitized) even when we don't have a response
                self._safe_log(
                    req,
                    None,
                    correlation_id=correlation_id,
                    duration_ms=duration_ms,
                    retry_attempt=attempt_num,
                )
                self._log_attempt_failed(
                    correlation_id=correlation_id,
                    retry_attempt=attempt_num,
                    duration_ms=duration_ms,
                    exc=exc,
                )

                if attempt_num >= attempts:
                    # Final: GIVE UP
                    self._log_give_up(correlation_id=correlation_id, attempts=attempts, exc=exc)
                    raise

                # Compute next sleep (exponential) and retry
                sleep_seconds = min(
                    max(multiplier * (2 ** (attempt_num - 1)), min_sleep), max_sleep
                )
                self._log_retry_sleep(
                    correlation_id=correlation_id,
                    retry_attempt=attempt_num,
                    sleep_seconds=sleep_seconds,
                )
                time.sleep(sleep_seconds)

            except Exception as exc:
                # Non-retryable error: log request and give up immediately
                duration_ms = int((time.perf_counter() - start) * 1000)

                self._safe_log(
                    req,
                    None,
                    correlation_id=correlation_id,
                    duration_ms=duration_ms,
                    retry_attempt=attempt_num,
                )
                self._log_give_up(correlation_id=correlation_id, attempts=attempt_num, exc=exc)
                raise

        # Should be unreachable, but keep a safe fallback.
        raise RuntimeError("Request failed without an exception (unexpected)")

    def get(self, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        return self.request("GET", path, auth=auth, **kwargs)

    def post(self, path: str, *, auth: bool = False, **kwargs) -> httpx.Response:
        return self.request("POST", path, auth=auth, **kwargs)
