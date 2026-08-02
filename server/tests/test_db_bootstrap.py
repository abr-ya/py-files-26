"""Database bootstrap compatibility tests."""

from __future__ import annotations

from sqlalchemy import create_engine, text

from py_files_server.db import _ensure_sqlite_upload_session_columns


def test_init_backfills_legacy_upload_session_columns(tmp_path) -> None:
    db_path = tmp_path / "legacy.sqlite"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE upload_sessions (
                    id CHAR(32) NOT NULL PRIMARY KEY,
                    owner_user_id CHAR(32) NOT NULL,
                    expected_size BIGINT NOT NULL,
                    received_bytes BIGINT NOT NULL,
                    partial_storage_path VARCHAR(2048) NOT NULL,
                    state VARCHAR(32) NOT NULL,
                    created_at DATETIME NOT NULL
                )
                """
            )
        )

    _ensure_sqlite_upload_session_columns(engine)

    with engine.connect() as connection:
        columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(upload_sessions)")).all()
        }

    assert "original_filename" in columns
    assert "sha256" in columns
