"""Phase 7: TTL-expired rows do not expose metadata or octet-stream."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient

from py_files_server.db import SessionLocal
from py_files_server.models.stored_object import StoredUploadObject


def test_expired_meta_and_content_yield_404_not_in_list(client: TestClient) -> None:
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"login": "ttluser", "password": "ttl-secret-123"},
        ).status_code
        == 201
    )
    lr = client.post("/api/v1/auth/login", json={"login": "ttluser", "password": "ttl-secret-123"})
    hdr = {"Authorization": f"Bearer {lr.json()['access_token']}"}

    up = client.post(
        "/api/v1/objects",
        headers=hdr,
        files={"file": ("ttl.bin", b"still-on-disk-until-manual-delete", "application/octet-stream")},
    )
    assert up.status_code == 201
    oid_str = up.json()["id"]
    oid = UUID(oid_str)

    with SessionLocal() as db:
        row = db.get(StoredUploadObject, oid)
        assert row is not None
        row.expires_at = datetime.now(tz=UTC) - timedelta(days=1)
        db.commit()

    assert client.get("/api/v1/objects", headers=hdr).status_code == 200
    assert oid_str not in {x["id"] for x in client.get("/api/v1/objects", headers=hdr).json()}

    assert client.get(f"/api/v1/objects/{oid_str}", headers=hdr).status_code == 404
    assert (
        client.get(f"/api/v1/objects/{oid_str}/content", headers=hdr).status_code == 404
    )
