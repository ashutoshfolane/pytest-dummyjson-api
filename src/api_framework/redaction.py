from __future__ import annotations

from typing import Any

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie"}

SENSITIVE_JSON_KEYS = {
    "accessToken",
    "refreshToken",
    "token",
    "idToken",
    "session",
    "password",
}


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers.items():
        if k.lower() in SENSITIVE_HEADERS:
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out


def redact_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: "***REDACTED***" if k in SENSITIVE_JSON_KEYS else redact_json(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact_json(x) for x in obj]
    return obj
