"""Finalize resumable upload sessions into stored objects."""

from __future__ import annotations

import hashlib
import shutil
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from py_files_server.models.stored_object import StoredUploadObject
from py_files_server.models.upload_session import UploadSession, UploadSessionState
from py_files_server.services.fs_storage import relative_blob_path, resolve_under_root
from py_files_server.settings import Settings

_READ_CHUNK = 1024 * 1024


class UploadFinalizeError(Exception):
    """Raised when a session cannot be completed."""


class UploadChecksumMismatch(UploadFinalizeError):
    """Raised when the uploaded file does not match the requested checksum."""


def _sha256_file(path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(_READ_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def finalize_upload_session(
    db: Session,
    session: UploadSession,
    settings: Settings,
) -> StoredUploadObject:
    """Promote a complete partial upload into the permanent blob layout."""
    if session.state != UploadSessionState.ACTIVE.value:
        raise UploadFinalizeError("Upload session is not active")
    if session.received_bytes != session.expected_size:
        raise UploadFinalizeError("Upload session has not received all bytes")

    partial_path = resolve_under_root(settings.storage_root, session.partial_storage_path)
    if not partial_path.is_file():
        raise UploadFinalizeError("Upload session partial file is missing")

    actual_sha256 = _sha256_file(partial_path)
    if session.sha256 is not None and actual_sha256.lower() != session.sha256.lower():
        raise UploadChecksumMismatch("Uploaded file checksum does not match")

    object_id = uuid.uuid4()
    rel = relative_blob_path("blobs", str(object_id))
    dest = resolve_under_root(settings.storage_root, rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(partial_path), dest)

    created_at = datetime.now(tz=UTC)
    row = StoredUploadObject(
        id=object_id,
        owner_user_id=session.owner_user_id,
        original_filename=session.original_filename,
        byte_size=session.received_bytes,
        storage_path=rel,
        sha256=actual_sha256,
        created_at=created_at,
        expires_at=created_at + timedelta(days=settings.retention_days),
    )
    session.state = UploadSessionState.COMPLETED.value
    session.partial_storage_path = ""
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

