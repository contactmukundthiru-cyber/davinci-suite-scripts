from pathlib import Path
from typing import Any

from core.jsonschema import validate_json
from core.fs import load_json
from core.config import Config


class PackError(ValueError):
    pass


def load_mapping_pack(path: Path, cfg: Config) -> dict[str, Any]:
    data = load_json(path)
    schema_path = cfg.schema_dir / "mapping_pack.schema.json"
    validate_json(data, schema_path)
    return data


def load_brand_pack(path: Path, cfg: Config) -> dict[str, Any]:
    data = load_json(path)
    schema_path = cfg.schema_dir / "brand_pack.schema.json"
    validate_json(data, schema_path)
    return data


def load_delivery_pack(path: Path, cfg: Config) -> dict[str, Any]:
    data = load_json(path)
    schema_path = cfg.schema_dir / "delivery_pack.schema.json"
    validate_json(data, schema_path)
    return data
