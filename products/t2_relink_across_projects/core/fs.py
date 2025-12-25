import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Union


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()


def atomic_write(path: Path, data: str, encoding: str = "utf-8") -> None:
    path = normalize_path(path)
    ensure_dir(path.parent)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(data)
        tmp_path.replace(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def safe_copy(src: Path, dst: Path, overwrite: bool = False) -> None:
    src = normalize_path(src)
    dst = normalize_path(dst)
    ensure_dir(dst.parent)
    if dst.exists() and not overwrite:
        raise FileExistsError(f"Destination exists: {dst}")
    shutil.copy2(src, dst)


def safe_move(src: Path, dst: Path, overwrite: bool = False) -> None:
    src = normalize_path(src)
    dst = normalize_path(dst)
    ensure_dir(dst.parent)
    if dst.exists() and not overwrite:
        raise FileExistsError(f"Destination exists: {dst}")
    shutil.move(str(src), str(dst))


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, data: Any, indent: int = 2) -> None:
    atomic_write(path, json.dumps(data, indent=indent, ensure_ascii=True))


def load_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()
