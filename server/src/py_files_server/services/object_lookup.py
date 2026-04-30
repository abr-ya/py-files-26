"""Shared stored-object access checks (owner, expiry, disk presence)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from py_files_server.models.stored_object import StoredUploadObject
from py_files_server.models.user import User
from py_files_server.services.fs_storage import resolve_under_root
from py_files_server.settings import Settings


def _as_utc(dt: datetime) -> datetime:
    """Normalize ORM/datetime coming from SQLite (often naive UTC) for comparisons."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def get_owned_object_or_none(
    db: Session,
    settings: Settings,
    current_user: User,
    object_id: uuid.UUID,
    *,
    require_non_expired: bool,
) -> StoredUploadObject | None:
    """Return row if owned, on disk, and (when required) not past ``expires_at``."""
    row = db.get(StoredUploadObject, object_id)
    if row is None or row.owner_user_id != current_user.id:
        return None
    now = datetime.now(tz=UTC)
    if require_non_expired and _as_utc(row.expires_at) < now:
        return None
    path = resolve_under_root(settings.storage_root, row.storage_path)
    if not path.is_file():
        return None
    return row


def list_objects_for_owner(
    db: Session,
    current_user: User,
    settings: Settings,
) -> list[StoredUploadObject]:
    """Non-expired objects for the current user, newest first, with blob present."""
    now = datetime.now(tz=UTC)
    stmt: Select[tuple[StoredUploadObject]] = (
        select(StoredUploadObject)
        .where(StoredUploadObject.owner_user_id == current_user.id)
        .where(StoredUploadObject.expires_at >= now)
        .order_by(StoredUploadObject.created_at.desc())
    )
    rows = list(db.scalars(stmt).all())
    out: list[StoredUploadObject] = []
    for row in rows:
        try:
            blob = resolve_under_root(settings.storage_root, row.storage_path)
        except ValueError:
            continue
        if blob.is_file():
            out.append(row)
    return out
