"""Database engine, sessions, and schema bootstrap."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from py_files_server.settings import Settings, get_settings


def _sqlite_connect_args(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def make_engine(settings: Settings) -> Engine:
    engine = create_engine(
        settings.database_url,
        connect_args=_sqlite_connect_args(settings.database_url),
        pool_pre_ping=True,
    )
    if settings.database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _sqlite_foreign_keys(dbapi_connection, connection_record) -> None:  # noqa: ARG001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


_settings_for_engine = get_settings()
engine = make_engine(_settings_for_engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create tables if they do not exist (MVP — Alembic later)."""
    # Import models so metadata registers tables before create_all.
    import py_files_server.models.stored_object  # noqa: F401
    import py_files_server.models.upload_session  # noqa: F401
    import py_files_server.models.user  # noqa: F401
    from py_files_server.models.base import Base

    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_upload_session_columns(engine)


def _ensure_sqlite_upload_session_columns(bind: Engine) -> None:
    """Backfill additive SQLite dev-schema columns until Alembic exists."""
    if not bind.url.drivername.startswith("sqlite"):
        return

    inspector = inspect(bind)
    if "upload_sessions" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("upload_sessions")}
    statements: list[str] = []
    if "original_filename" not in existing_columns:
        statements.append(
            "ALTER TABLE upload_sessions "
            "ADD COLUMN original_filename VARCHAR(1024) NOT NULL DEFAULT 'upload.bin'"
        )
    if "sha256" not in existing_columns:
        statements.append("ALTER TABLE upload_sessions ADD COLUMN sha256 VARCHAR(64)")

    if not statements:
        return

    with bind.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
