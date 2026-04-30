"""``pyfiles download`` — fetch object bytes (owner only)."""

from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import requests

from py_files_cli.config_store import default_config_path, load_config


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download a stored object (authenticated).")
    p.add_argument("object_id", type=uuid.UUID, help="Object UUID returned after upload")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Destination file path (default: from Content-Disposition or '<id>.bin')",
    )
    p.add_argument(
        "--base-url",
        default=None,
        help="Override server root URL (default: from config)",
    )
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help=f"Config file path (default: {default_config_path()})",
    )
    return p


def _filename_from_content_disposition(value: str | None, fallback: str) -> str:
    if not value:
        return fallback
    m = re.search(r'filename\*=UTF-8\'\'([^;]+)', value)
    if m:
        decoded = unquote(m.group(1).strip())
        return Path(decoded).name.strip() or fallback
    m2 = re.search(r'filename="([^"]+)"', value)
    if m2:
        return Path(m2.group(1)).name.strip() or fallback
    m3 = re.search(r"filename=([^;\s]+)", value)
    if m3:
        return Path(m3.group(1).strip().strip('"')).name or fallback
    return fallback


def run(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    cfg_path = Path(args.config).expanduser() if args.config else default_config_path()
    cfg: dict[str, Any] = load_config(cfg_path)
    token = cfg.get("access_token")
    base = (args.base_url or cfg.get("base_url") or "http://127.0.0.1:8000").rstrip("/")
    if not token:
        print(
            "download failed: no access_token in config. Run pyfiles login first.",
            file=sys.stderr,
        )
        return 1

    url = f"{base}/api/v1/objects/{args.object_id}/content"
    try:
        with requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            stream=True,
            timeout=300,
        ) as r:
            if r.status_code != 200:
                print(f"download failed: HTTP {r.status_code} — {r.text}", file=sys.stderr)
                return 1
            fname = _filename_from_content_disposition(
                r.headers.get("content-disposition"),
                f"{args.object_id}.bin",
            )
            out = args.output
            if out is None:
                out = Path(fname)
            else:
                out = out.expanduser()

            out.parent.mkdir(parents=True, exist_ok=True)

            wrote = 0
            with out.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        fh.write(chunk)
                        wrote += len(chunk)
            print(f"Wrote {wrote} bytes to {out.resolve()}")
    except requests.RequestException as exc:
        print(f"download failed: network error — {exc}", file=sys.stderr)
        return 1
    return 0
