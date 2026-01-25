from __future__ import annotations

from .config import Settings


def validate_settings(s: Settings) -> None:
    # Base config
    if not str(s.base_url).startswith(("http://", "https://")):
        raise ValueError("BASE_URL must start with http:// or https://")

    if s.timeout_seconds <= 0:
        raise ValueError("TIMEOUT_SECONDS must be > 0")

    if s.retry_attempts < 0:
        raise ValueError("RETRY_ATTEMPTS must be >= 0")

    # Auth config:
    # Allow either:
    # 1) AUTH_HEADER_VALUE (fast path token), OR
    # 2) AUTH_USERNAME + AUTH_PASSWORD (login path), OR
    # 3) neither (public-only runs)
    if s.auth_header_value:
        return

    if (s.auth_username and not s.auth_password) or (s.auth_password and not s.auth_username):
        raise ValueError(
            "Provide both AUTH_USERNAME and AUTH_PASSWORD, or provide AUTH_HEADER_VALUE"
        )
