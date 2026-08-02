"""Local CLI configuration helpers."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class CliConfig:
    base_url: str | None = None
    access_token: str | None = None


def normalize_base_url(value: str) -> str:
    """Return a normalized HTTP(S) base URL without a trailing slash."""
    cleaned = value.strip().rstrip("/")
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("--base-url must be an absolute http(s) URL")
    return cleaned


def config_dir() -> Path:
    """Return the py-files config directory, overridable for tests."""
    override = os.environ.get("PY_FILES_CONFIG_HOME")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "py-files"
    return Path.home() / ".config" / "py-files"


def config_path() -> Path:
    return config_dir() / "config.json"


def upload_retry_dir() -> Path:
    return config_dir() / "upload-retries"


def load_config() -> CliConfig:
    path = config_path()
    if not path.exists():
        return CliConfig()
    data = json.loads(path.read_text(encoding="utf-8"))
    return CliConfig(
        base_url=data.get("base_url"),
        access_token=data.get("access_token"),
    )


def save_config(config: CliConfig) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "base_url": config.base_url,
                "access_token": config.access_token,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
