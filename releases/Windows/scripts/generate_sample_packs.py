from pathlib import Path

from core.config import get_config, ensure_dirs
from core.fs import load_json, save_json


SAMPLES = {
    "mapping_pack": "presets/mapping_pack.example.json",
    "brand_pack": "presets/brand_pack.example.json",
    "delivery_pack": "presets/delivery_pack.example.json",
}


def main() -> None:
    cfg = get_config()
    ensure_dirs(cfg)
    for name, src in SAMPLES.items():
        data = load_json(Path(src))
        save_json(cfg.packs_dir / f"{name}.json", data)
    print(f"Sample packs written to {cfg.packs_dir}")


if __name__ == "__main__":
    main()
