"""Phase 7: login → multipart upload → list → download (integration-level)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_login_upload_list_download_round_trip(client: TestClient) -> None:
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"login": "roundtrip", "password": "pw-roundtrip-123"},
        ).status_code
        == 201
    )

    lr = client.post("/api/v1/auth/login", json={"login": "roundtrip", "password": "pw-roundtrip-123"})
    assert lr.status_code == 200
    token = lr.json()["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}

    blob = b"roundtrip-payload-binary"

    up = client.post(
        "/api/v1/objects",
        headers=hdr,
        files={"file": ("roundtrip.bin", blob, "application/octet-stream")},
    )
    assert up.status_code == 201
    meta = up.json()
    oid = meta["id"]
    assert meta["byte_size"] == len(blob)

    lst = client.get("/api/v1/objects", headers=hdr)
    assert lst.status_code == 200
    ids = [x["id"] for x in lst.json()]
    assert oid in ids

    dl = client.get(f"/api/v1/objects/{oid}/content", headers=hdr)
    assert dl.status_code == 200
    assert dl.content == blob
