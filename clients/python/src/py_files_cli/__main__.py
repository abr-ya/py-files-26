"""Entry point for ``pyfiles`` console script."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from py_files_cli.commands.login import add_login_parser
from py_files_cli.commands.status import add_status_parser
from py_files_cli.commands.upload import add_upload_parser
from py_files_cli.config import normalize_base_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyfiles",
        description="CLI client for py-files upload/download.",
    )
    parser.add_argument(
        "--base-url",
        help="py-files API base URL, for example http://127.0.0.1:8000",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_login_parser(subparsers)
    add_status_parser(subparsers)
    add_upload_parser(subparsers)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.base_url is not None:
        args.base_url = normalize_base_url(args.base_url)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
