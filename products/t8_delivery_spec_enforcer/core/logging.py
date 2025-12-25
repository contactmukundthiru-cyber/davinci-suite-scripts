import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.config import Config


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key.startswith("rps_"):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=True)


class HumanFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = f"{record.levelname:<7} {record.name}: {record.getMessage()}"
        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"
        return base


def setup_logging(cfg: Config) -> None:
    cfg.logs_dir.mkdir(parents=True, exist_ok=True)
    json_path = cfg.logs_dir / "rps.jsonl"
    human_path = cfg.logs_dir / "rps.log"

    root = logging.getLogger()
    root.setLevel(cfg.log_level)
    root.handlers.clear()

    json_handler = logging.FileHandler(json_path, encoding="utf-8")
    json_handler.setFormatter(JsonLineFormatter())

    human_handler = logging.FileHandler(human_path, encoding="utf-8")
    human_handler.setFormatter(HumanFormatter())

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(HumanFormatter())

    root.addHandler(json_handler)
    root.addHandler(human_handler)
    root.addHandler(stream_handler)


def get_logger(name: str, **context: Any) -> logging.LoggerAdapter:
    logger = logging.getLogger(name)
    extra = {f"rps_{k}": v for k, v in context.items() if v is not None}
    return logging.LoggerAdapter(logger, extra)


def log_path(cfg: Config) -> Path:
    return cfg.logs_dir / "rps.log"
