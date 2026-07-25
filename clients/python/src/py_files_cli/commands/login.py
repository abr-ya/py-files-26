"""Login command."""

from __future__ import annotations

import argparse
import getpass
import sys

import requests

from py_files_cli.config import CliConfig, save_config


def add_login_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("login", help="Authenticate and save local CLI config")
    parser.add_argument("--login", help="Account login")
    parser.add_argument("--password", help="Account password")
    parser.set_defaults(func=run_login)


def _prompt_if_missing(value: str | None, prompt: str, *, secret: bool = False) -> str:
    if value:
        return value
    if secret:
        return getpass.getpass(prompt)
    return input(prompt)


def run_login(args: argparse.Namespace) -> int:
    if args.base_url is None:
        print("error: login requires --base-url", file=sys.stderr)
        return 2

    login = _prompt_if_missing(args.login, "Login: ")
    password = _prompt_if_missing(args.password, "Password: ", secret=True)
    response = requests.post(
        f"{args.base_url}/api/v1/auth/login",
        json={"login": login, "password": password},
        timeout=30,
    )
    if response.status_code != 200:
        print(f"error: login failed ({response.status_code})", file=sys.stderr)
        return 1

    token = response.json().get("access_token")
    if not token:
        print("error: login response did not include access_token", file=sys.stderr)
        return 1

    save_config(CliConfig(base_url=args.base_url, access_token=token))
    print(f"Logged in to {args.base_url}")
    return 0

