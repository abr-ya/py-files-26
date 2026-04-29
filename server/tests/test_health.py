"""Smoke tests — Phase 2 foundation."""

from fastapi.testclient import TestClient

from py_files_server.main import app


def test_health_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
