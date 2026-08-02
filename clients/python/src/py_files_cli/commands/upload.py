"""Resumable upload command."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

from py_files_cli.config import load_config, upload_retry_dir

_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class _UploadTarget:
    base_url: str
    token: str


@dataclass(frozen=True)
class _FileIdentity:
    path: str
    size: int
    modified_ns: int


@dataclass
class _RetryMetadata:
    path: str
    size: int
    modified_ns: int
    base_url: str
    session_id: str
    expected_size: int
    offset: int


def add_upload_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("upload", help="Upload a local file with resumable sessions")
    parser.add_argument("path", help="Local file path to upload")
    parser.set_defaults(func=run_upload)


def _resolve_upload_target(args: argparse.Namespace) -> _UploadTarget | None:
    config = load_config()
    base_url = args.base_url or config.base_url
    if base_url is None:
        print("error: upload requires --base-url or saved login config", file=sys.stderr)
        return None
    if not config.access_token:
        print("error: upload requires saved login token; run pyfiles --base-url <url> login", file=sys.stderr)
        return None
    return _UploadTarget(base_url=base_url, token=config.access_token)


def _file_identity(path: Path) -> _FileIdentity:
    stat = path.stat()
    return _FileIdentity(
        path=str(path.resolve()),
        size=stat.st_size,
        modified_ns=stat.st_mtime_ns,
    )


def _metadata_path(identity: _FileIdentity, base_url: str) -> Path:
    key = hashlib.sha256(f"{base_url}\0{identity.path}".encode("utf-8")).hexdigest()
    return upload_retry_dir() / f"{key}.json"


def _load_retry_metadata(identity: _FileIdentity, base_url: str) -> _RetryMetadata | None:
    path = _metadata_path(identity, base_url)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    metadata = _RetryMetadata(**data)
    if (
        metadata.path != identity.path
        or metadata.size != identity.size
        or metadata.modified_ns != identity.modified_ns
        or metadata.base_url != base_url
        or metadata.expected_size != identity.size
    ):
        return None
    return metadata


def _save_retry_metadata(identity: _FileIdentity, metadata: _RetryMetadata) -> None:
    path = _metadata_path(identity, metadata.base_url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(metadata), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _delete_retry_metadata(identity: _FileIdentity, base_url: str) -> None:
    path = _metadata_path(identity, base_url)
    if path.exists():
        path.unlink()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _create_upload_session(target: _UploadTarget, path: Path, identity: _FileIdentity) -> _RetryMetadata | None:
    try:
        response = requests.post(
            f"{target.base_url}/api/v1/upload-sessions",
            json={
                "filename": path.name,
                "total_size": identity.size,
                "sha256": _sha256_file(path),
            },
            headers={"Authorization": f"Bearer {target.token}"},
            timeout=30,
        )
    except requests.RequestException as exc:
        print(f"error: failed to create upload session: {exc}", file=sys.stderr)
        return None

    if response.status_code != 201:
        print(f"error: failed to create upload session ({response.status_code}): {response.text}", file=sys.stderr)
        return None

    body = response.json()
    metadata = _RetryMetadata(
        path=identity.path,
        size=identity.size,
        modified_ns=identity.modified_ns,
        base_url=target.base_url,
        session_id=body["id"],
        expected_size=body.get("expected_size", identity.size),
        offset=body.get("received_bytes", 0),
    )
    _save_retry_metadata(identity, metadata)
    return metadata


def _expected_offset(response: requests.Response) -> int | None:
    try:
        detail = response.json().get("detail", {})
    except ValueError:
        return None
    expected = detail.get("expected_offset") if isinstance(detail, dict) else None
    return expected if isinstance(expected, int) and expected >= 0 else None


def _append_chunks(target: _UploadTarget, local_path: Path, identity: _FileIdentity, metadata: _RetryMetadata) -> bool:
    offset = metadata.offset
    with local_path.open("rb") as source:
        source.seek(offset)
        while offset < identity.size:
            chunk = source.read(_CHUNK_SIZE)
            if not chunk:
                break
            try:
                response = requests.patch(
                    f"{target.base_url}/api/v1/upload-sessions/{metadata.session_id}",
                    data=chunk,
                    headers={
                        "Authorization": f"Bearer {target.token}",
                        "Content-Type": "application/octet-stream",
                        "Upload-Offset": str(offset),
                    },
                    timeout=30,
                )
            except requests.RequestException as exc:
                metadata.offset = offset
                _save_retry_metadata(identity, metadata)
                print(f"error: upload interrupted: {exc}", file=sys.stderr)
                return False

            if response.status_code == 204:
                offset += len(chunk)
                metadata.offset = offset
                _save_retry_metadata(identity, metadata)
                print(f"uploaded {offset}/{identity.size} bytes")
                continue

            if response.status_code == 409:
                expected = _expected_offset(response)
                if expected is not None and expected <= identity.size:
                    offset = expected
                    metadata.offset = offset
                    _save_retry_metadata(identity, metadata)
                    source.seek(offset)
                    continue

            print(f"error: upload chunk failed ({response.status_code}): {response.text}", file=sys.stderr)
            return False
    return True


def _complete_upload(target: _UploadTarget, metadata: _RetryMetadata) -> dict[str, object] | None:
    try:
        response = requests.post(
            f"{target.base_url}/api/v1/upload-sessions/{metadata.session_id}/complete",
            headers={"Authorization": f"Bearer {target.token}"},
            timeout=30,
        )
    except requests.RequestException as exc:
        print(f"error: failed to complete upload: {exc}", file=sys.stderr)
        return None

    if response.status_code != 201:
        print(f"error: failed to complete upload ({response.status_code}): {response.text}", file=sys.stderr)
        return None
    return response.json()


def run_upload(args: argparse.Namespace) -> int:
    target = _resolve_upload_target(args)
    if target is None:
        return 2

    local_path = Path(args.path)
    if not local_path.is_file():
        print(f"error: local file not found: {local_path}", file=sys.stderr)
        return 2

    identity = _file_identity(local_path)
    metadata = _load_retry_metadata(identity, target.base_url)
    if metadata is None:
        metadata = _create_upload_session(target, local_path, identity)
        if metadata is None:
            return 1

    if not _append_chunks(target, local_path, identity, metadata):
        return 1

    result = _complete_upload(target, metadata)
    if result is None:
        return 1

    _delete_retry_metadata(identity, target.base_url)
    object_id = result.get("id")
    if object_id:
        print(f"uploaded: {object_id}")
    else:
        print("uploaded")
    return 0
