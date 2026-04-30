"""``pyfiles`` CLI entry — dispatch ``login`` and ``upload`` subcommands."""

from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "usage: pyfiles {login|upload} ...",
            file=sys.stderr,
        )
        print(
            "  pyfiles login --login USER --password PASS [--base-url URL]",
            file=sys.stderr,
        )
        print(
            "  pyfiles upload [--resume] [--chunk-size N] FILE",
            file=sys.stderr,
        )
        sys.exit(2)
    cmd = sys.argv[1]
    rest = sys.argv[2:]
    if cmd == "login":
        from py_files_cli.commands.login import run as login_run

        sys.exit(login_run(rest))
    if cmd == "upload":
        from py_files_cli.commands.upload import run as upload_run

        sys.exit(upload_run(rest))
    print(f"unknown command: {cmd}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
