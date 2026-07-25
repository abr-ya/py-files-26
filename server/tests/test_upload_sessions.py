"""Resumable upload-session API tests."""

from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient

from py_files_server.main import app
from py_files_server.settings import Settings, get_settings


def _register_and_login(client: TestClient, login: str = "session-user") -> str:
    password = "secretpw"
    r = client.post("/api/v1/auth/register", json={"login": login, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/auth/login", json={"login": login, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_append_and_complete_upload_session() -> None:
    payload = b"hello resumable"
    checksum = hashlib.sha256(payload).hexdigest()

    with TestClient(app) as client:
        token = _register_and_login(client, login="session-happy")
        r = client.post(
            "/api/v1/upload-sessions",
            json={"filename": "hello.txt", "total_size": len(payload), "sha256": checksum},
            headers=_auth(token),
        )
        assert r.status_code == 201, r.text
        session = r.json()
        assert session["received_bytes"] == 0
        assert session["expected_size"] == len(payload)

        r = client.patch(
            f"/api/v1/upload-sessions/{session['id']}",
            content=payload,
            headers={**_auth(token), "Upload-Offset": "0", "Content-Type": "application/octet-stream"},
        )
        assert r.status_code == 204, r.text

        r = client.post(f"/api/v1/upload-sessions/{session['id']}/complete", headers=_auth(token))
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["original_filename"] == "hello.txt"
        assert body["byte_size"] == len(payload)
        assert "id" in body


def test_append_rejects_offset_mismatch() -> None:
    with TestClient(app) as client:
        token = _register_and_login(client, login="session-offset")
        r = client.post(
            "/api/v1/upload-sessions",
            json={"filename": "file.bin", "total_size": 10},
            headers=_auth(token),
        )
        session_id = r.json()["id"]

        r = client.patch(
            f"/api/v1/upload-sessions/{session_id}",
            content=b"abc",
            headers={**_auth(token), "Upload-Offset": "1", "Content-Type": "application/octet-stream"},
        )
        assert r.status_code == 409
        assert r.json()["detail"]["expected_offset"] == 0


def test_complete_rejects_incomplete_session() -> None:
    with TestClient(app) as client:
        token = _register_and_login(client, login="session-incomplete")
        r = client.post(
            "/api/v1/upload-sessions",
            json={"filename": "file.bin", "total_size": 5},
            headers=_auth(token),
        )
        session_id = r.json()["id"]

        r = client.post(f"/api/v1/upload-sessions/{session_id}/complete", headers=_auth(token))
        assert r.status_code == 409
        assert "not received all bytes" in r.json()["detail"]


def test_other_user_cannot_append_session() -> None:
    with TestClient(app) as client:
        owner_token = _register_and_login(client, login="session-owner")
        other_token = _register_and_login(client, login="session-other")
        r = client.post(
            "/api/v1/upload-sessions",
            json={"filename": "file.bin", "total_size": 3},
            headers=_auth(owner_token),
        )
        session_id = r.json()["id"]

        r = client.patch(
            f"/api/v1/upload-sessions/{session_id}",
            content=b"abc",
            headers={**_auth(other_token), "Upload-Offset": "0", "Content-Type": "application/octet-stream"},
        )
        assert r.status_code == 404


def test_create_session_rejects_over_limit() -> None:
    def low_cap_settings() -> Settings:
        return Settings(max_upload_bytes=5)

    with TestClient(app) as client:
        app.dependency_overrides[get_settings] = low_cap_settings
        try:
            token = _register_and_login(client, login="session-big")
            r = client.post(
                "/api/v1/upload-sessions",
                json={"filename": "big.bin", "total_size": 6},
                headers=_auth(token),
            )
            assert r.status_code == 413
            assert "maximum" in r.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(get_settings, None)

def test_append_rejects_over_expected_size() -> None:
    with TestClient(app) as client:
        token = _register_and_login(client, login="session-too-much")
        r = client.post(
            "/api/v1/upload-sessions",
            json={"filename": "small.bin", "total_size": 2},
            headers=_auth(token),
        )
        session_id = r.json()["id"]

        r = client.patch(
            f"/api/v1/upload-sessions/{session_id}",
            content=b"abc",
            headers={**_auth(token), "Upload-Offset": "0", "Content-Type": "application/octet-stream"},
        )
        assert r.status_code == 413

