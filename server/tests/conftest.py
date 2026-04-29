"""Pytest fixtures for API tests (Phase 1: httpx client to running server).

Phase 2+ may add ``ASGITransport`` fixtures once ``py_files_server.main:app`` exists.
"""

from __future__ import annotations

import os
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
