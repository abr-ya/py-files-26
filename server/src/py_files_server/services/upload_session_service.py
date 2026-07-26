"""Service helpers for resumable upload sessions."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy.orm import Session

from py_files_server.models.upload_session import UploadSession, UploadSessionState
from py_files_server.models.user import User
from py_files_server.services.fs_storage import relative_blob_path, resolve_under_root
from py_files_server.settings import Settings


class UploadSessionError(Exception):
    """Base exception for upload-session service failures."""


class UploadSessionNotFound(UploadSessionError):
    """Raised when the session does not exist for the current owner."""


class UploadSessionInactive(UploadSessionError):
    """Raised when an append/complete operation targets an inactive session."""


class UploadOffsetMismatch(UploadSessionError):
    """Raised when the client sends a non-contiguous chunk offset."""

    def __init__(self, expected_offset: int) -> None:
        self.expected_offset = expected_offset
        super().__init__(f"Expected upload offset {expected_offset}")


class UploadTooLarge(UploadSessionError):
    """Raised when requested or appended bytes exceed server/session limits."""


def safe_original_filename(name: str) -> str:
    """Return a compact basename safe for metadata display."""
    base = Path(name).name.strip()
    if not base or base in {".", ".."}:
        return "upload.bin"
    return base[:1024]


def create_upload_session(
    db: Session,
    user: User,
    filename: str,
    total_size: int,
    sha256: str | None,
    settings: Settings,
) -> UploadSession:
    """Create an owned resumable upload session with an empty partial file."""
    if total_size > settings.max_upload_bytes:
        raise UploadTooLarge("Upload exceeds maximum allowed size")

    session_id = uuid.uuid4()
    rel = relative_blob_path("partials", f"{session_id}.part")
    partial_path = resolve_under_root(settings.storage_root, rel)
    partial_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path.touch(exist_ok=False)

    session = UploadSession(
        id=session_id,
        owner_user_id=user.id,
        original_filename=safe_original_filename(filename),
        expected_size=total_size,
        received_bytes=0,
        partial_storage_path=rel,
        sha256=sha256.lower() if sha256 is not None else None,
        state=UploadSessionState.ACTIVE.value,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_owned_upload_session(db: Session, user: User, session_id: uuid.UUID) -> UploadSession:
    """Return an upload session owned by ``user`` or raise a 404-shaped error."""
    session = db.get(UploadSession, session_id)
    if session is None or session.owner_user_id != user.id:
        raise UploadSessionNotFound("Upload session not found")
    return session


async def append_upload_chunk(
    db: Session,
    session: UploadSession,
    offset: int,
    chunks: AsyncIterator[bytes],
    settings: Settings,
) -> UploadSession:
    """Append request bytes to a session only when the offset is contiguous."""
    if session.state != UploadSessionState.ACTIVE.value:
        raise UploadSessionInactive("Upload session is not active")
    if offset != session.received_bytes:
        raise UploadOffsetMismatch(session.received_bytes)

    written = session.received_bytes
    partial_path = resolve_under_root(settings.storage_root, session.partial_storage_path)
    partial_path.parent.mkdir(parents=True, exist_ok=True)

    with partial_path.open("ab") as out:
        async for chunk in chunks:
            if not chunk:
                continue
            next_total = written + len(chunk)
            if next_total > session.expected_size or next_total > settings.max_upload_bytes:
                raise UploadTooLarge("Chunk exceeds expected upload size")
            out.write(chunk)
            written = next_total

    session.received_bytes = written
    db.commit()
    db.refresh(session)
    return session

