"""Phase 5: list metadata and octet-stream download."""

from __future__ import annotations

from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from py_files_server.db import engine
from py_files_server.models.base import Base
from py_files_server.services.fs_storage import ensure_storage_layout
from py_files_server.settings import get_settings


@pytest.fixture(autouse=True)
def _reset() -> None:
    settings = get_settings()
    if settings.storage_root.exists():
        import shutil

        shutil.rmtree(settings.storage_root)
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    ensure_storage_layout(settings.storage_root)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> TestClient:
    from py_files_server.main import app

    return TestClient(app)


@pytest.fixture
def alice(client: TestClient) -> tuple[dict[str, str], str]:
    assert client.post(
        "/api/v1/auth/register",
        json={"login": "alice", "password": "secret123"},
    ).status_code == 201
    lr = client.post("/api/v1/auth/login", json={"login": "alice", "password": "secret123"})
    assert lr.status_code == 200
    token = lr.json()["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}
    return hdr, token


@pytest.fixture
def bob(client: TestClient) -> dict[str, str]:
    client.post("/api/v1/auth/register", json={"login": "bob", "password": "secret123"})
    lr = client.post("/api/v1/auth/login", json={"login": "bob", "password": "secret123"})
    token = lr.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_empty_then_upload_then_list_download(client: TestClient, alice: tuple) -> None:
    hdr, _ = alice
    li = client.get("/api/v1/objects", headers=hdr)
    assert li.status_code == 200
    assert li.json() == []

    up = client.post(
        "/api/v1/objects",
        headers=hdr,
        files={"file": ("readme.txt", b"hello world", "text/plain")},
    )
    assert up.status_code == 201
    oid_str = up.json()["id"]
    oid = UUID(oid_str)

    li2 = client.get("/api/v1/objects", headers=hdr)
    assert li2.status_code == 200
    body = li2.json()
    assert len(body) == 1
    assert body[0]["id"] == oid_str
    assert body[0]["original_filename"] == "readme.txt"
    assert body[0]["byte_size"] == 11

    m = client.get(f"/api/v1/objects/{oid}", headers=hdr)
    assert m.status_code == 200
    assert m.json()["byte_size"] == 11

    dl = client.get(f"/api/v1/objects/{oid}/content", headers=hdr)
    assert dl.status_code == 200
    assert dl.content == b"hello world"
    assert "application/octet-stream" in (dl.headers.get("content-type") or "")


def test_download_other_owner_is_404(client: TestClient, alice: tuple, bob: dict[str, str]) -> None:
    hdr, _ = alice
    up = client.post(
        "/api/v1/objects",
        headers=hdr,
        files={"file": ("a.bin", b"x", "application/octet-stream")},
    )
    assert up.status_code == 201
    oid = up.json()["id"]

    for path in (
        f"/api/v1/objects/{oid}",
        f"/api/v1/objects/{oid}/content",
    ):
        assert client.get(path, headers=bob).status_code == 404
