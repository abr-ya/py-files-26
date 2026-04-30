"""Entry point for ``pyfiles`` console script (Phases 2+ implement commands)."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pyfiles",
        description="CLI client for py-files upload/download (commands arrive in Phase 2+).",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
