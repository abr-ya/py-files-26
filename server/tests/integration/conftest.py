"""Reset DB + STORAGE_ROOT between Phase 7 integration scenarios."""

from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from py_files_server.db import engine
from py_files_server.models.base import Base
from py_files_server.services.fs_storage import ensure_storage_layout
from py_files_server.settings import get_settings


@pytest.fixture(autouse=True)
def _integration_reset() -> None:
    settings = get_settings()
    if settings.storage_root.exists():
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
