"""API tests for resumable upload sessions (Phase 4 / US2)."""

from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from py_files_server.db import engine
from py_files_server.models.base import Base
from py_files_server.services.fs_storage import ensure_storage_layout
from py_files_server.settings import get_settings


@pytest.fixture(autouse=True)
def _reset_tables() -> None:
    settings = get_settings()
    if settings.storage_root.exists():
        shutil.rmtree(settings.storage_root)
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    ensure_storage_layout(settings.storage_root)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    from py_files_server.main import app

    return TestClient(app)


def _register_and_login(client: TestClient) -> tuple[dict[str, str], str]:
    r = client.post(
        "/api/v1/auth/register",
        json={"login": "cliuser", "password": "secret123"},
    )
    assert r.status_code == 201
    lr = client.post("/api/v1/auth/login", json={"login": "cliuser", "password": "secret123"})
    assert lr.status_code == 200
    token = lr.json()["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}
    return hdr, token


def test_upload_session_round_trip(client: TestClient) -> None:
    hdr, _ = _register_and_login(client)
    payload = b"hello-resume-world"

    cr = client.post(
        "/api/v1/upload-sessions",
        headers=hdr,
        json={"filename": "demo.bin", "total_size": len(payload)},
    )
    assert cr.status_code == 201
    session_id = cr.json()["id"]

    g = client.get(f"/api/v1/upload-sessions/{session_id}", headers=hdr)
    assert g.status_code == 200
    assert g.json()["received_bytes"] == 0

    p1 = client.patch(
        f"/api/v1/upload-sessions/{session_id}",
        headers={**hdr, "Upload-Offset": "0"},
        content=payload[:5],
    )
    assert p1.status_code == 204

    bad = client.patch(
        f"/api/v1/upload-sessions/{session_id}",
        headers={**hdr, "Upload-Offset": "0"},
        content=b"xx",
    )
    assert bad.status_code == 409

    p2 = client.patch(
        f"/api/v1/upload-sessions/{session_id}",
        headers={**hdr, "Upload-Offset": "5"},
        content=payload[5:],
    )
    assert p2.status_code == 204

    fin = client.post(f"/api/v1/upload-sessions/{session_id}/complete", headers=hdr)
    assert fin.status_code == 201
    body = fin.json()
    assert body["byte_size"] == len(payload)
    assert body["original_filename"] == "demo.bin"

    meta = client.get(f"/api/v1/upload-sessions/{session_id}", headers=hdr)
    assert meta.status_code == 404


def test_create_session_over_max_returns_413(client: TestClient) -> None:
    hdr, _ = _register_and_login(client)
    r = client.post(
        "/api/v1/upload-sessions",
        headers=hdr,
        json={"filename": "huge.bin", "total_size": 10**9 + 1},
    )
    assert r.status_code == 413
