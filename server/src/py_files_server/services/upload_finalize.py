"""Finalize resumable upload sessions into stored objects."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from py_files_server.models.stored_object import StoredUploadObject
from py_files_server.models.upload_session import UploadSession, UploadSessionState
from py_files_server.models.user import User
from py_files_server.services.upload_session_service import UploadSessionConflict, get_session_for_owner
from py_files_server.services.fs_storage import relative_blob_path, resolve_under_root
from py_files_server.settings import Settings

_DIGEST_CHUNK = 1024 * 1024


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(_DIGEST_CHUNK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def complete_session(
    db: Session,
    owner: User,
    session_id: uuid.UUID,
    settings: Settings,
) -> StoredUploadObject:
    """Validate size, checksum, move blob, create ``StoredUploadObject``, remove session."""
    row = get_session_for_owner(db, owner, session_id, require_active=True)

    if row.received_bytes != row.expected_size:
        raise UploadSessionConflict(
            "Upload session is incomplete; append remaining bytes before completing.",
        )

    partial_path = resolve_under_root(settings.storage_root, row.partial_storage_path)
    if not partial_path.is_file():
        row.state = UploadSessionState.FAILED.value
        db.add(row)
        db.commit()
        raise UploadSessionConflict("Partial payload missing on disk; session marked failed.")

    sha256_hex = _sha256_file(partial_path)

    object_id = uuid.uuid4()
    rel_blob = relative_blob_path("blobs", str(object_id))
    blob_path = resolve_under_root(settings.storage_root, rel_blob)
    blob_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        partial_path.rename(blob_path)
    except OSError:
        # Cross-device fallback
        blob_path.write_bytes(partial_path.read_bytes())
        partial_path.unlink(missing_ok=True)

    created_at = datetime.now(tz=UTC)
    expires_at = created_at + timedelta(days=settings.retention_days)

    stored = StoredUploadObject(
        id=object_id,
        owner_user_id=owner.id,
        original_filename=row.original_filename,
        byte_size=row.expected_size,
        storage_path=rel_blob,
        sha256=sha256_hex,
        created_at=created_at,
        expires_at=expires_at,
    )

    db.delete(row)
    db.add(stored)
    db.commit()
    db.refresh(stored)
    return stored
