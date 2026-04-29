"""Pytest fixtures for API tests (Phase 1: httpx client to running server).

Phase 2+ may add ``ASGITransport`` fixtures once ``py_files_server.main:app`` exists.
"""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile

_pytest_home = tempfile.mkdtemp(prefix="py-files-pytest-")
os.environ["DATABASE_URL"] = f"sqlite:///{_pytest_home}/db.sqlite"
os.environ["STORAGE_ROOT"] = f"{_pytest_home}/storage"
os.environ["JWT_SECRET"] = "pytest-secret-fixed"


def _cleanup_pytest_home() -> None:
    shutil.rmtree(_pytest_home, ignore_errors=True)


atexit.register(_cleanup_pytest_home)

from collections.abc import AsyncIterator

import pytest
from httpx import AsyncClient

_DEFAULT_BASE = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for integration tests (override via ``PY_FILES_TEST_API``)."""
    return os.environ.get("PY_FILES_TEST_API", _DEFAULT_BASE)


@pytest.fixture
async def async_client(api_base_url: str) -> AsyncIterator[AsyncClient]:
    """Async HTTP client aimed at the API base URL (defaults to ``http://127.0.0.1:8000``)."""
    async with AsyncClient(base_url=api_base_url, timeout=30.0) as client:
        yield client
