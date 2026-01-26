# API contracts
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_schema(schema_path: str | Path) -> dict[str, Any]:
    path = Path(schema_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json_schema(payload: Any, schema_path: str | Path) -> None:
    """
    Validates `payload` against a JSON Schema file using Draft 2020-12 validator.
    Raises jsonschema.ValidationError on mismatch.
    """
    schema = load_schema(schema_path)
    Draft202012Validator(schema).validate(payload)
