"""Resolve paths safely under STORAGE_ROOT."""

from __future__ import annotations

from pathlib import Path


def ensure_storage_layout(storage_root: Path) -> None:
    """Create canonical subdirectories for blobs and partial uploads."""
    (storage_root / "blobs").mkdir(parents=True, exist_ok=True)
    (storage_root / "partials").mkdir(parents=True, exist_ok=True)


def resolve_under_root(storage_root: Path, relative_path: str) -> Path:
    """Resolve ``relative_path`` safely under ``storage_root``."""
    root = storage_root.resolve()
    target = (root / relative_path).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path escapes storage root") from exc
    return target


def relative_blob_path(collection: str, filename: str) -> str:
    """Return POSIX-style relative path segment ``collection/filename``."""
    safe_collection = collection.strip("/").replace("..", "")
    safe_name = filename.replace("..", "").lstrip("/")
    return f"{safe_collection}/{safe_name}"
