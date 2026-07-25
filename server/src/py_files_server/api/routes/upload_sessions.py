"""Resumable upload-session routes."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from py_files_server.api.deps import get_current_user
from py_files_server.api.schemas.objects import StoredObjectMeta
from py_files_server.api.schemas.upload_sessions import UploadSessionCreate, UploadSessionPublic
from py_files_server.db import get_db
from py_files_server.models.stored_object import StoredUploadObject
from py_files_server.models.upload_session import UploadSession
from py_files_server.models.user import User
from py_files_server.services.upload_finalize import (
    UploadChecksumMismatch,
    UploadFinalizeError,
    finalize_upload_session,
)
from py_files_server.services.upload_session_service import (
    UploadOffsetMismatch,
    UploadSessionInactive,
    UploadSessionNotFound,
    UploadTooLarge,
    append_upload_chunk,
    create_upload_session,
    get_owned_upload_session,
)
from py_files_server.settings import Settings, get_settings

router = APIRouter(tags=["UploadSessions"])


async def _single_body_chunk(body: bytes) -> AsyncIterator[bytes]:
    if body:
        yield body


def _max_size_detail(max_bytes: int) -> str:
    return (
        f"File exceeds maximum allowed size ({max_bytes} bytes). "
        "Choose a smaller file or ask an administrator to raise the limit."
    )


def _get_session_or_404(db: Session, current_user: User, session_id: uuid.UUID) -> UploadSession:
    try:
        return get_owned_upload_session(db, current_user, session_id)
    except UploadSessionNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload session not found",
        ) from exc


@router.post("", response_model=UploadSessionPublic, status_code=status.HTTP_201_CREATED)
def create_session(
    body: UploadSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UploadSession:
    """Create an owned resumable upload session."""
    try:
        return create_upload_session(
            db=db,
            user=current_user,
            filename=body.filename,
            total_size=body.total_size,
            sha256=body.sha256,
            settings=settings,
        )
    except UploadTooLarge as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=_max_size_detail(settings.max_upload_bytes),
        ) from exc


@router.patch("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def append_chunk(
    session_id: uuid.UUID,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    upload_offset: Annotated[int, Header(alias="Upload-Offset", ge=0)],
) -> Response:
    """Append a contiguous octet-stream chunk to an active session."""
    session = _get_session_or_404(db, current_user, session_id)
    try:
        body = await request.body()
        await append_upload_chunk(db, session, upload_offset, _single_body_chunk(body), settings)
    except UploadOffsetMismatch as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Upload offset mismatch", "expected_offset": exc.expected_offset},
        ) from exc
    except UploadSessionInactive as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Upload session is not active",
        ) from exc
    except UploadTooLarge as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=_max_size_detail(min(session.expected_size, settings.max_upload_bytes)),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{session_id}/complete",
    response_model=StoredObjectMeta,
    status_code=status.HTTP_201_CREATED,
)
def complete_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> StoredUploadObject:
    """Finalize an uploaded session into a stored object."""
    session = _get_session_or_404(db, current_user, session_id)
    try:
        return finalize_upload_session(db, session, settings)
    except UploadChecksumMismatch as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uploaded file checksum does not match",
        ) from exc
    except UploadFinalizeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
