import json
from pathlib import Path
from typing import Any

from core.fs import load_json

try:
    import jsonschema as _jsonschema
except Exception:  # pragma: no cover - optional dependency
    _jsonschema = None


class SchemaValidationError(ValueError):
    pass


def load_schema(schema_path: Path) -> dict[str, Any]:
    return load_json(schema_path)


def validate_json(data: Any, schema_path: Path) -> None:
    if _jsonschema is None:
        raise SchemaValidationError(
            "jsonschema library not installed. Install with: pip install jsonschema"
        )
    schema = load_schema(schema_path)
    try:
        _jsonschema.validate(instance=data, schema=schema)
    except _jsonschema.ValidationError as exc:
        raise SchemaValidationError(str(exc)) from exc


def validate_json_text(text: str, schema_path: Path) -> Any:
    data = json.loads(text)
    validate_json(data, schema_path)
    return data
