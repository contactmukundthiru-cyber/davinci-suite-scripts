from pathlib import Path
from typing import Any

from core.config import Config
from core.fs import ensure_dir, load_json, save_json


class PresetError(ValueError):
    pass


def _preset_dir(cfg: Config, tool_id: str) -> Path:
    return cfg.presets_dir / tool_id


def list_presets(cfg: Config, tool_id: str) -> list[str]:
    preset_dir = _preset_dir(cfg, tool_id)
    if not preset_dir.exists():
        return []
    return sorted([p.stem for p in preset_dir.glob("*.json")])


def save_preset(cfg: Config, tool_id: str, name: str, options: dict[str, Any]) -> Path:
    preset_dir = _preset_dir(cfg, tool_id)
    ensure_dir(preset_dir)
    path = preset_dir / f"{name}.json"
    save_json(path, {"tool_id": tool_id, "name": name, "options": options})
    return path


def load_preset(cfg: Config, tool_id: str, name: str) -> dict[str, Any]:
    path = _preset_dir(cfg, tool_id) / f"{name}.json"
    if not path.exists():
        raise PresetError(f"Preset not found: {name}")
    data = load_json(path)
    if data.get("tool_id") and data.get("tool_id") != tool_id:
        raise PresetError(f"Preset tool mismatch: {data.get('tool_id')} != {tool_id}")
    return data.get("options", {})
