"""Stored object routes (`/objects`)."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from py_files_server.api.deps import get_current_user
from py_files_server.api.schemas.objects import StoredObjectMeta
from py_files_server.db import get_db
from py_files_server.models.stored_object import StoredUploadObject
from py_files_server.models.user import User
from py_files_server.services.fs_storage import relative_blob_path, resolve_under_root
from py_files_server.services.object_lookup import (
    get_owned_object_or_none,
    list_objects_for_owner,
)
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


_OBJECT_GONE_DETAIL = "Object not found or no longer available."


def _basename_for_attachment(name: str) -> str:
    base = Path(name).name.strip()
    if not base or base in {".", ".."}:
        return "download.bin"
    return base[:255]


@router.get("", response_model=list[StoredObjectMeta])
def list_stored_objects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[StoredUploadObject]:
    """List non-expired objects for the authenticated user."""
    return list_objects_for_owner(db, current_user, settings)


@router.get("/{object_id}", response_model=StoredObjectMeta)
def get_stored_object_meta(
    object_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> StoredUploadObject:
    row = get_owned_object_or_none(
        db,
        settings,
        current_user,
        object_id,
        require_non_expired=True,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_OBJECT_GONE_DETAIL)
    return row


@router.get("/{object_id}/content")
def download_stored_object(
    object_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FileResponse:
    row = get_owned_object_or_none(
        db,
        settings,
        current_user,
        object_id,
        require_non_expired=True,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_OBJECT_GONE_DETAIL)
    path = resolve_under_root(settings.storage_root, row.storage_path)
    fname = _basename_for_attachment(row.original_filename)
    return FileResponse(
        path=str(path),
        filename=fname,
        media_type="application/octet-stream",
    )


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
