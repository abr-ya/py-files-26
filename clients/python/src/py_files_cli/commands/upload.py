"""``pyfiles upload`` — resumable chunked upload (upload-sessions API)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

from py_files_cli.config_store import default_config_path, load_config

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # type: ignore[misc, assignment]


def _sidecar_path(file_path: Path) -> Path:
    return file_path.with_name(f"{file_path.name}.pyfiles-session")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Upload a file using resumable sessions.")
    p.add_argument(
        "--base-url",
        default=None,
        help="Override server root URL (default: from config or http://127.0.0.1:8000)",
    )
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help=f"Config file path (default: {default_config_path()})",
    )
    p.add_argument(
        "--chunk-size",
        type=int,
        default=8 * 1024 * 1024,
        metavar="N",
        help="Bytes per PATCH chunk (default: 8 MiB)",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Continue using sidecar session next to the file",
    )
    p.add_argument("file", type=Path, help="Local file path to upload")
    return p


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _session_from_config(cfg_path: Path | None) -> tuple[str, str]:
    cfg = load_config(cfg_path)
    token = cfg.get("access_token")
    base = cfg.get("base_url") or "http://127.0.0.1:8000"
    base = base.rstrip("/")
    if not token:
        raise ValueError(
            "No access_token in config. Run: pyfiles login --login USER --password PASS",
        )
    return base, str(token)


def run(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    file_path: Path = args.file.expanduser().resolve()
    if args.chunk_size < 1:
        print("upload failed: --chunk-size must be at least 1", file=sys.stderr)
        return 1

    cfg_path = Path(args.config).expanduser() if args.config else default_config_path()

    try:
        base, token = _session_from_config(cfg_path)
    except ValueError as exc:
        print(f"upload failed: {exc}", file=sys.stderr)
        return 1
    if args.base_url:
        base = args.base_url.rstrip("/")

    sidecar = _sidecar_path(file_path)

    if not file_path.is_file():
        print(f"upload failed: not a file: {file_path}", file=sys.stderr)
        return 1

    sz = file_path.stat().st_size

    sess: dict[str, Any]
    if args.resume:
        if not sidecar.is_file():
            print(f"upload failed: no sidecar at {sidecar}", file=sys.stderr)
            return 1
        with sidecar.open(encoding="utf-8") as fh:
            sess = json.load(fh)
        session_id = sess["session_id"]
        meta_url = f"{base}/api/v1/upload-sessions/{session_id}"
        mr = requests.get(meta_url, headers=_headers(token), timeout=60)
        if mr.status_code != 200:
            print(f"upload failed: resume metadata HTTP {mr.status_code} — {mr.text}", file=sys.stderr)
            return 1
        prog = mr.json()
        expected = int(prog["expected_size"])
        if expected != sz:
            print(
                "upload failed: file size changed since session was created",
                file=sys.stderr,
            )
            return 1
        sent = int(prog["received_bytes"])
    else:
        if sidecar.is_file():
            print(
                f"upload failed: session sidecar exists ({sidecar}). "
                "Use --resume or remove the sidecar.",
                file=sys.stderr,
            )
            return 1
        cre = requests.post(
            f"{base}/api/v1/upload-sessions",
            headers=_headers(token),
            json={"filename": file_path.name, "total_size": sz},
            timeout=60,
        )
        if cre.status_code != 201:
            print(f"upload failed: create session HTTP {cre.status_code} — {cre.text}", file=sys.stderr)
            return 1
        cre_json = cre.json()
        session_id = cre_json["id"]
        sent = 0
        sess = {
            "session_id": session_id,
            "filename": file_path.name,
            "expected_size": sz,
            "base_url": base,
        }
        with sidecar.open("w", encoding="utf-8") as fh:
            json.dump(sess, fh, indent=2)
            fh.write("\n")

    total_to_send = sz - sent
    cr: requests.Response | None = None
    bar = tqdm(total=total_to_send, unit="B", unit_scale=True) if tqdm and total_to_send > 0 else None
    try:
        with file_path.open("rb") as fh_data:
            fh_data.seek(sent)
            while sent < sz:
                chunk = fh_data.read(args.chunk_size)
                if not chunk:
                    break
                url = f"{base}/api/v1/upload-sessions/{session_id}"
                pr = requests.patch(
                    url,
                    headers={**_headers(token), "Upload-Offset": str(sent)},
                    data=chunk,
                    timeout=300,
                )
                if pr.status_code != 204:
                    print(
                        f"upload failed: PATCH HTTP {pr.status_code} at offset {sent} — {pr.text}",
                        file=sys.stderr,
                    )
                    return 1
                sent += len(chunk)
                if bar:
                    bar.update(len(chunk))

            if sent != sz:
                print("upload failed: short read from local file", file=sys.stderr)
                return 1

            cr = requests.post(
                f"{base}/api/v1/upload-sessions/{session_id}/complete",
                headers=_headers(token),
                timeout=120,
            )
            if cr.status_code != 201:
                print(f"upload failed: complete HTTP {cr.status_code} — {cr.text}", file=sys.stderr)
                return 1
    finally:
        if bar:
            bar.close()

    try:
        sidecar.unlink(missing_ok=True)
    except OSError:
        pass

    if cr is not None:
        print(cr.json())
    return 0
