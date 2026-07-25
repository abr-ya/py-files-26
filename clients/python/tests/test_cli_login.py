"""CLI login/config tests."""

from __future__ import annotations

import json
from pathlib import Path

from py_files_cli.__main__ import main
from py_files_cli.config import config_path, normalize_base_url


class _Response:
    status_code = 200

    def json(self) -> dict[str, str]:
        return {"access_token": "token-123"}


def test_normalize_base_url_strips_trailing_slash() -> None:
    assert normalize_base_url("http://127.0.0.1:8000/") == "http://127.0.0.1:8000"


def test_login_requires_base_url(capsys) -> None:
    code = main(["login", "--login", "u1", "--password", "secretpw"])

    assert code == 2
    assert "requires --base-url" in capsys.readouterr().err


def test_login_saves_base_url_and_token(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def fake_post(url: str, json: dict[str, str], timeout: int):
        seen["url"] = url
        seen["json"] = json
        seen["timeout"] = timeout
        return _Response()

    monkeypatch.setenv("PY_FILES_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("py_files_cli.commands.login.requests.post", fake_post)

    code = main(
        [
            "--base-url",
            "http://127.0.0.1:8000/",
            "login",
            "--login",
            "u1",
            "--password",
            "secretpw",
        ]
    )

    assert code == 0
    assert seen == {
        "url": "http://127.0.0.1:8000/api/v1/auth/login",
        "json": {"login": "u1", "password": "secretpw"},
        "timeout": 30,
    }
    assert json.loads(config_path().read_text(encoding="utf-8")) == {
        "access_token": "token-123",
        "base_url": "http://127.0.0.1:8000",
    }

