"""CLI resumable upload tests."""

from __future__ import annotations

import json
from pathlib import Path

import requests

from py_files_cli.__main__ import main
from py_files_cli.config import upload_retry_dir


class _Response:
    def __init__(
        self,
        status_code: int,
        *,
        body: dict[str, object] | None = None,
        text: str = "",
    ) -> None:
        self.status_code = status_code
        self._body = body or {}
        self.text = text

    def json(self) -> dict[str, object]:
        return self._body


def _write_config(tmp_path: Path, *, base_url: str = "http://server.test", token: str | None = "token-123") -> None:
    (tmp_path / "config.json").write_text(
        json.dumps({"base_url": base_url, "access_token": token}),
        encoding="utf-8",
    )


def test_upload_requires_base_url_before_reading_file(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))

    code = main(["upload", str(tmp_path / "missing.bin")])

    assert code == 2
    assert "requires --base-url or saved login config" in capsys.readouterr().err


def test_upload_requires_saved_token(monkeypatch, tmp_path: Path, capsys) -> None:
    local_file = tmp_path / "file.bin"
    local_file.write_bytes(b"hello")
    _write_config(tmp_path, token=None)
    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))

    code = main(["upload", str(local_file)])

    assert code == 2
    assert "requires saved login token" in capsys.readouterr().err


def test_upload_uses_saved_config_and_completes(monkeypatch, tmp_path: Path, capsys) -> None:
    local_file = tmp_path / "hello.txt"
    local_file.write_bytes(b"hello")
    _write_config(tmp_path)
    seen: dict[str, object] = {"patches": []}

    def fake_post(url: str, **kwargs):
        if url.endswith("/api/v1/upload-sessions"):
            seen["create_url"] = url
            seen["create_json"] = kwargs["json"]
            seen["create_headers"] = kwargs["headers"]
            return _Response(
                201,
                body={
                    "id": "session-1",
                    "received_bytes": 0,
                    "expected_size": 5,
                    "state": "active",
                },
            )
        seen["complete_url"] = url
        seen["complete_headers"] = kwargs["headers"]
        return _Response(201, body={"id": "object-1"})

    def fake_patch(url: str, **kwargs):
        seen["patches"].append(
            {
                "url": url,
                "data": kwargs["data"],
                "headers": kwargs["headers"],
            }
        )
        return _Response(204)

    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.upload.requests.post", fake_post)
    monkeypatch.setattr("py_files_cli.commands.upload.requests.patch", fake_patch)

    code = main(["upload", str(local_file)])

    assert code == 0
    assert seen["create_url"] == "http://server.test/api/v1/upload-sessions"
    assert seen["create_json"]["filename"] == "hello.txt"
    assert seen["create_json"]["total_size"] == 5
    assert seen["create_headers"] == {"Authorization": "Bearer token-123"}
    assert seen["patches"] == [
        {
            "url": "http://server.test/api/v1/upload-sessions/session-1",
            "data": b"hello",
            "headers": {
                "Authorization": "Bearer token-123",
                "Content-Type": "application/octet-stream",
                "Upload-Offset": "0",
            },
        }
    ]
    assert seen["complete_url"] == "http://server.test/api/v1/upload-sessions/session-1/complete"
    assert "uploaded: object-1" in capsys.readouterr().out
    assert list(upload_retry_dir().glob("*.json")) == []


def test_upload_uses_explicit_base_url_with_saved_token(monkeypatch, tmp_path: Path) -> None:
    local_file = tmp_path / "hello.txt"
    local_file.write_bytes(b"hello")
    _write_config(tmp_path, base_url="http://saved.test")
    seen: dict[str, object] = {"patches": []}

    def fake_post(url: str, **kwargs):
        if url.endswith("/api/v1/upload-sessions"):
            seen["create_url"] = url
            return _Response(201, body={"id": "session-1", "received_bytes": 0, "expected_size": 5})
        return _Response(201, body={"id": "object-1"})

    def fake_patch(url: str, **kwargs):
        seen["patches"].append(url)
        return _Response(204)

    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.upload.requests.post", fake_post)
    monkeypatch.setattr("py_files_cli.commands.upload.requests.patch", fake_patch)

    code = main(["--base-url", "http://explicit.test", "upload", str(local_file)])

    assert code == 0
    assert seen["create_url"] == "http://explicit.test/api/v1/upload-sessions"
    assert seen["patches"] == ["http://explicit.test/api/v1/upload-sessions/session-1"]


def test_upload_updates_offset_after_mismatch(monkeypatch, tmp_path: Path) -> None:
    local_file = tmp_path / "hello.txt"
    local_file.write_bytes(b"hello")
    _write_config(tmp_path)
    offsets: list[str] = []

    def fake_post(url: str, **kwargs):
        if url.endswith("/api/v1/upload-sessions"):
            return _Response(201, body={"id": "session-1", "received_bytes": 0, "expected_size": 5})
        return _Response(201, body={"id": "object-1"})

    def fake_patch(url: str, **kwargs):
        offset = kwargs["headers"]["Upload-Offset"]
        offsets.append(offset)
        if offset == "0":
            return _Response(409, body={"detail": {"message": "Upload offset mismatch", "expected_offset": 2}})
        return _Response(204)

    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.upload.requests.post", fake_post)
    monkeypatch.setattr("py_files_cli.commands.upload.requests.patch", fake_patch)

    code = main(["upload", str(local_file)])

    assert code == 0
    assert offsets == ["0", "2"]


def test_upload_preserves_retry_metadata_after_interruption(monkeypatch, tmp_path: Path, capsys) -> None:
    local_file = tmp_path / "hello.txt"
    local_file.write_bytes(b"hello")
    _write_config(tmp_path)

    def fake_post(url: str, **kwargs):
        return _Response(201, body={"id": "session-1", "received_bytes": 0, "expected_size": 5})

    def fake_patch(url: str, **kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.upload.requests.post", fake_post)
    monkeypatch.setattr("py_files_cli.commands.upload.requests.patch", fake_patch)

    code = main(["upload", str(local_file)])

    assert code == 1
    assert "upload interrupted" in capsys.readouterr().err
    retry_files = list(upload_retry_dir().glob("*.json"))
    assert len(retry_files) == 1
    metadata = json.loads(retry_files[0].read_text(encoding="utf-8"))
    assert metadata["session_id"] == "session-1"
    assert metadata["offset"] == 0
