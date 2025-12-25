import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

APP_NAME = "resolve_production_suite"
ENV_PREFIX = "RPS"


def _xdg_path(env_var: str, default: str) -> Path:
    value = os.environ.get(env_var)
    if value:
        return Path(value)
    return Path(default).expanduser()


@dataclass
class Config:
    app_name: str = APP_NAME
    home_dir: Path = _xdg_path("RPS_HOME", "~/.rps")
    data_dir: Path = _xdg_path("XDG_DATA_HOME", "~/.local/share") / APP_NAME
    config_dir: Path = _xdg_path("XDG_CONFIG_HOME", "~/.config") / APP_NAME
    cache_dir: Path = _xdg_path("XDG_CACHE_HOME", "~/.cache") / APP_NAME
    logs_dir: Path = _xdg_path("RPS_LOGS", "~/.rps/logs")
    reports_dir: Path = _xdg_path("RPS_REPORTS", "~/.rps/reports")
    presets_dir: Path = _xdg_path("RPS_PRESETS", "~/.rps/presets")
    packs_dir: Path = _xdg_path("RPS_PACKS", "~/.rps/packs")
    schema_dir: Path = Path(__file__).resolve().parent.parent / "schemas"
    sample_dir: Path = Path(__file__).resolve().parent.parent / "sample_data"
    resolve_script_api: Optional[Path] = None
    log_level: str = "INFO"
    dry_run: bool = False

    def __post_init__(self) -> None:
        env_script_api = os.environ.get("RESOLVE_SCRIPT_API")
        if env_script_api:
            self.resolve_script_api = Path(env_script_api)


_default_config: Optional[Config] = None


def get_config() -> Config:
    global _default_config
    if _default_config is None:
        _default_config = Config()
    return _default_config


def ensure_dirs(cfg: Config) -> None:
    for path in [cfg.home_dir, cfg.data_dir, cfg.config_dir, cfg.cache_dir,
                 cfg.logs_dir, cfg.reports_dir, cfg.presets_dir, cfg.packs_dir]:
        path.mkdir(parents=True, exist_ok=True)


def resolve_script_paths(cfg: Config) -> list[Path]:
    paths: list[Path] = []
    if cfg.resolve_script_api:
        paths.append(cfg.resolve_script_api)
    env_paths = os.environ.get("RPS_RESOLVE_PYTHON_PATHS", "")
    for raw in env_paths.split(":" if os.name != "nt" else ";"):
        raw = raw.strip()
        if raw:
            paths.append(Path(raw).expanduser())
    return paths
