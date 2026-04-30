"""Shared CLI config path and JSON load/save."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def default_config_path() -> Path:
    """Return path to ``~/.config/py-files/config.json`` (``%APPDATA%`` on Windows)."""
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "py-files" / "config.json"
    return Path.home() / ".config" / "py-files" / "config.json"


def load_config(path: Path | None = None) -> dict[str, Any]:
    p = path or default_config_path()
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def save_config(data: dict[str, Any], path: Path | None = None) -> None:
    p = path or default_config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
