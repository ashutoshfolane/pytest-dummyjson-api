from .config import Settings


def validate_settings(s: Settings) -> None:
    if not str(s.base_url).startswith("http"):
        raise ValueError("BASE_URL must start with http/https")
