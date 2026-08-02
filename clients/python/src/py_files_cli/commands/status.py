"""Remote server status command."""

from __future__ import annotations

import argparse
import sys

import requests

from py_files_cli.config import load_config


def add_status_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("status", help="Check configured remote server health")
    parser.set_defaults(func=run_status)


def _resolve_base_url(args: argparse.Namespace) -> str | None:
    if args.base_url is not None:
        return args.base_url
    return load_config().base_url


def run_status(args: argparse.Namespace) -> int:
    base_url = _resolve_base_url(args)
    if base_url is None:
        print("error: status requires --base-url or saved login config", file=sys.stderr)
        return 2

    try:
        response = requests.get(f"{base_url}/health", timeout=10)
    except requests.RequestException as exc:
        print(f"error: server status check failed: {exc}", file=sys.stderr)
        return 1

    if response.status_code != 200:
        print(f"error: server status check failed ({response.status_code})", file=sys.stderr)
        return 1

    print(f"ok: {base_url}")
    return 0
