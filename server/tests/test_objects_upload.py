"""Multipart upload (User Story 1)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from py_files_server.main import app
from py_files_server.settings import Settings, get_settings


def _register_and_login(client: TestClient, login: str = "u1", password: str = "secretpw") -> str:
    r = client.post("/api/v1/auth/register", json={"login": login, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/auth/login", json={"login": login, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_post_object_multipart() -> None:
    with TestClient(app) as client:
        token = _register_and_login(client)
        files = {"file": ("hello.txt", b"hello world", "text/plain")}
        r = client.post(
            "/api/v1/objects",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["byte_size"] == 11
        assert body["original_filename"] == "hello.txt"
        assert "id" in body


def test_post_object_rejects_over_limit() -> None:
    def low_cap_settings() -> Settings:
        return Settings(max_upload_bytes=5)

    with TestClient(app) as client:
        app.dependency_overrides[get_settings] = low_cap_settings
        try:
            token = _register_and_login(client, login="u2")
            files = {"file": ("big.bin", b"1234567890abcdef", "application/octet-stream")}
            r = client.post(
                "/api/v1/objects",
                files=files,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 413
            detail = r.json().get("detail", "")
            assert isinstance(detail, str)
            low = detail.lower()
            assert "maximum" in low or "exceeds" in low or "allowed" in low
        finally:
            app.dependency_overrides.pop(get_settings, None)


def test_index_serves_ui() -> None:
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")
        assert "upload" in r.text.lower()
