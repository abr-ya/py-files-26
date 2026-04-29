"""Stored object routes (`/objects`)."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from py_files_server.api.deps import get_current_user
from py_files_server.api.schemas.objects import StoredObjectMeta
from py_files_server.db import get_db
from py_files_server.models.stored_object import StoredUploadObject
from py_files_server.models.user import User
from py_files_server.services.fs_storage import relative_blob_path, resolve_under_root
from py_files_server.settings import Settings, get_settings

router = APIRouter(tags=["Objects"])

_READ_CHUNK = 1024 * 1024  # 1 MiB


def _safe_original_filename(name: str | None) -> str:
    if not name:
        return "upload.bin"
    base = Path(name).name.strip()
    if not base or base in {".", ".."}:
        return "upload.bin"
    return base[:1024]


async def _stream_upload_to_disk(
    upload: UploadFile,
    dest: Path,
    max_bytes: int,
    digest,
) -> int:
    """Write upload stream to ``dest``; enforce ``max_bytes``; return bytes written."""
    written = 0
    with dest.open("wb") as out:
        while True:
            chunk = await upload.read(_READ_CHUNK)
            if not chunk:
                break
            next_total = written + len(chunk)
            if next_total > max_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=(
                        f"File exceeds maximum allowed size ({max_bytes} bytes). "
                        "Choose a smaller file or ask an administrator to raise the limit."
                    ),
                )
            digest.update(chunk)
            out.write(chunk)
            written += len(chunk)
    return written


@router.post("", response_model=StoredObjectMeta, status_code=status.HTTP_201_CREATED)
async def upload_object_simple(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File()],
) -> StoredUploadObject:
    """Multipart upload (single ``file`` field); stream to disk with size cap."""
    original_name = _safe_original_filename(file.filename)
    object_id = uuid.uuid4()
    rel = relative_blob_path("blobs", str(object_id))
    dest = resolve_under_root(settings.storage_root, rel)
    dest.parent.mkdir(parents=True, exist_ok=True)

    digest = hashlib.sha256()

    try:
        written = await _stream_upload_to_disk(file, dest, settings.max_upload_bytes, digest)
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise

    created_at = datetime.now(tz=UTC)
    expires_at = created_at + timedelta(days=settings.retention_days)

    row = StoredUploadObject(
        id=object_id,
        owner_user_id=current_user.id,
        original_filename=original_name,
        byte_size=written,
        storage_path=rel,
        sha256=digest.hexdigest(),
        created_at=created_at,
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
