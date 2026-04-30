"""Upload session routes (`/upload-sessions`) — CLI resumable path."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from py_files_server.api.deps import get_current_user
from py_files_server.api.schemas.objects import StoredObjectMeta
from py_files_server.api.schemas.upload_sessions import UploadSessionCreate, UploadSessionOut
from py_files_server.db import get_db
from py_files_server.models.user import User
from py_files_server.services.upload_finalize import complete_session
from py_files_server.services.upload_session_service import (
    UploadSessionConflict,
    UploadSessionLookupError,
    append_chunk,
    create_session,
    get_session_for_owner,
)
from py_files_server.settings import Settings, get_settings

router = APIRouter(tags=["UploadSessions"])


def _conflict(exc: UploadSessionConflict) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("", response_model=UploadSessionOut, status_code=status.HTTP_201_CREATED)
def create_upload_session(
    body: UploadSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UploadSessionOut:
    if body.total_size > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                f"Declared size exceeds maximum allowed ({settings.max_upload_bytes} bytes). "
                "Choose a smaller file or ask an administrator to raise the limit."
            ),
        )
    row = create_session(db, current_user, body.filename, body.total_size, settings)
    return UploadSessionOut.model_validate(row)


@router.get("/{session_id}", response_model=UploadSessionOut)
def get_upload_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UploadSessionOut:
    """Return progress for the authenticated owner (supports CLI resume)."""
    try:
        row = get_session_for_owner(db, current_user, session_id, require_active=False)
    except UploadSessionLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload session not found",
        ) from exc
    return UploadSessionOut.model_validate(row)


@router.patch("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def append_upload_chunk(
    session_id: uuid.UUID,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    upload_offset: Annotated[int, Header(alias="Upload-Offset")],
) -> Response:
    body = await request.body()
    try:
        append_chunk(db, current_user, session_id, upload_offset, body, settings)
    except UploadSessionLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload session not found",
        ) from exc
    except UploadSessionConflict as exc:
        raise _conflict(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{session_id}/complete", response_model=StoredObjectMeta, status_code=status.HTTP_201_CREATED)
def complete_upload_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> StoredObjectMeta:
    try:
        row = complete_session(db, current_user, session_id, settings)
    except UploadSessionLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload session not found",
        ) from exc
    except UploadSessionConflict as exc:
        raise _conflict(exc) from exc
    return StoredObjectMeta.model_validate(row)
