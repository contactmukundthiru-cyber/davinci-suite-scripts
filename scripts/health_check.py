from pathlib import Path

from core.config import get_config, ensure_dirs
from core.logging import setup_logging, get_logger
from core.packs import load_brand_pack, load_delivery_pack, load_mapping_pack


SAMPLES = {
    "mapping": "presets/mapping_pack.example.json",
    "brand": "presets/brand_pack.example.json",
    "delivery": "presets/delivery_pack.example.json",
}


def main() -> None:
    cfg = get_config()
    ensure_dirs(cfg)
    setup_logging(cfg)
    logger = get_logger("health")
    logger.info("Running health check")

    load_mapping_pack(Path(SAMPLES["mapping"]), cfg)
    load_brand_pack(Path(SAMPLES["brand"]), cfg)
    load_delivery_pack(Path(SAMPLES["delivery"]), cfg)

    print("Health check OK")


if __name__ == "__main__":
    main()
