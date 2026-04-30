"""Create and append contiguous chunks for resumable upload sessions."""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from py_files_server.models.upload_session import UploadSession, UploadSessionState
from py_files_server.models.user import User
from py_files_server.services.fs_storage import relative_blob_path, resolve_under_root
from py_files_server.settings import Settings


class UploadSessionConflict(Exception):
    """Raised when offset or session state violates resumable contract."""


class UploadSessionLookupError(KeyError):
    """Missing session or not owned by requester (do not expose to unauthorized users)."""


def safe_original_filename(name: str) -> str:
    """Derive stable display basename (matches objects route heuristic)."""
    base = Path(name).name.strip()
    if not base or base in {".", ".."}:
        return "upload.bin"
    return base[:1024]


def create_session(
    db: Session,
    owner: User,
    original_filename: str,
    expected_size: int,
    settings: Settings,
) -> UploadSession:
    """Create an empty partial file on disk and an ``UploadSession`` row."""
    sid = uuid.uuid4()
    rel_partial = relative_blob_path("partials", str(sid))
    dest = resolve_under_root(settings.storage_root, rel_partial)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.touch()

    row = UploadSession(
        id=sid,
        owner_user_id=owner.id,
        original_filename=safe_original_filename(original_filename),
        expected_size=expected_size,
        received_bytes=0,
        partial_storage_path=rel_partial,
        state=UploadSessionState.ACTIVE.value,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_session_for_owner(
    db: Session,
    owner: User,
    session_id: uuid.UUID,
    *,
    require_active: bool = False,
) -> UploadSession:
    """Load session if it exists for ``owner``. Raises UploadSessionLookupError otherwise."""
    row = db.get(UploadSession, session_id)
    if row is None or row.owner_user_id != owner.id:
        raise UploadSessionLookupError(session_id)

    if require_active and row.state != UploadSessionState.ACTIVE.value:
        raise UploadSessionConflict(f"Upload session cannot accept bytes in state `{row.state}`.")
    return row


def append_chunk(
    db: Session,
    owner: User,
    session_id: uuid.UUID,
    upload_offset: int,
    body: bytes,
    settings: Settings,
) -> None:
    """Append ``body`` at ``upload_offset`` (must equal ``received_bytes``)."""
    if upload_offset < 0:
        raise UploadSessionConflict("Upload-Offset must be non-negative.")

    row = get_session_for_owner(db, owner, session_id, require_active=True)

    if upload_offset != row.received_bytes:
        raise UploadSessionConflict(
            "Upload-Offset does not match the next expected byte position for this session."
        )

    remaining = row.expected_size - row.received_bytes
    if len(body) > remaining:
        raise UploadSessionConflict("Chunk would exceed the declared total size for this session.")

    path = resolve_under_root(settings.storage_root, row.partial_storage_path)
    with path.open("ab") as out:
        out.write(body)

    row.received_bytes += len(body)
    db.add(row)
    db.commit()
