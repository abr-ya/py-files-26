"""``pyfiles login`` — store JWT for subsequent commands."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import requests

from py_files_cli.config_store import default_config_path, load_config, save_config


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sign in and save access token locally.")
    p.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Server root URL (default: %(default)s)",
    )
    p.add_argument("--login", "-l", required=True, help="Account login")
    p.add_argument("--password", "-p", required=True, help="Account password")
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help=f"Config file path (default: {default_config_path()})",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    base = args.base_url.rstrip("/")
    url = f"{base}/api/v1/auth/login"
    try:
        r = requests.post(
            url,
            json={"login": args.login, "password": args.password},
            timeout=60,
        )
    except requests.RequestException as exc:
        print(f"login failed: network error — {exc}", file=sys.stderr)
        return 1

    if r.status_code != 200:
        print(f"login failed: HTTP {r.status_code} — {r.text}", file=sys.stderr)
        return 1

    data: dict[str, Any] = r.json()
    token = data.get("access_token")
    if not token:
        print("login failed: response missing access_token", file=sys.stderr)
        return 1

    cfg_path = Path(args.config) if args.config else default_config_path()
    cfg = load_config(cfg_path)
    cfg["base_url"] = base
    cfg["access_token"] = token
    save_config(cfg, cfg_path)
    print(f"Saved credentials to {cfg_path}")
    return 0
