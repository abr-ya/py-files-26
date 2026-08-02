"""CLI remote status tests."""

from __future__ import annotations

import json
from pathlib import Path

from py_files_cli.__main__ import main


class _Response:
    def __init__(self, status_code: int = 200) -> None:
        self.status_code = status_code


def test_status_requires_base_url_or_saved_config(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))

    code = main(["status"])

    assert code == 2
    assert "requires --base-url or saved login config" in capsys.readouterr().err


def test_status_checks_explicit_base_url(monkeypatch, tmp_path: Path, capsys) -> None:
    seen: dict[str, object] = {}

    def fake_get(url: str, timeout: int):
        seen["url"] = url
        seen["timeout"] = timeout
        return _Response()

    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.status.requests.get", fake_get)

    code = main(["--base-url", "http://127.0.0.1:8000/", "status"])

    assert code == 0
    assert seen == {"url": "http://127.0.0.1:8000/health", "timeout": 10}
    assert "ok: http://127.0.0.1:8000" in capsys.readouterr().out


def test_status_uses_saved_base_url(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def fake_get(url: str, timeout: int):
        seen["url"] = url
        seen["timeout"] = timeout
        return _Response()

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"base_url": "http://server.test", "access_token": "token-123"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.status.requests.get", fake_get)

    code = main(["status"])

    assert code == 0
    assert seen == {"url": "http://server.test/health", "timeout": 10}


def test_status_reports_unhealthy_response(monkeypatch, tmp_path: Path, capsys) -> None:
    def fake_get(url: str, timeout: int):
        return _Response(status_code=503)

    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.status.requests.get", fake_get)

    code = main(["--base-url", "http://127.0.0.1:8000", "status"])

    assert code == 1
    assert "failed (503)" in capsys.readouterr().err
