"""Delete expired stored objects (TTL) — filesystem blob then DB row."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from py_files_server.models.stored_object import StoredUploadObject
from py_files_server.services.fs_storage import resolve_under_root
from py_files_server.settings import Settings

logger = logging.getLogger(__name__)


def purge_expired_upload_objects(session: Session, settings: Settings) -> int:
    """Remove expired rows and backing files; returns deleted row count."""
    now = datetime.now(tz=UTC)
    stmt = select(StoredUploadObject).where(StoredUploadObject.expires_at < now)
    rows = session.scalars(stmt).all()
    deleted = 0
    for obj in rows:
        try:
            path = resolve_under_root(settings.storage_root, obj.storage_path)
            if path.is_file():
                path.unlink()
                logger.info(
                    "Removed expired blob path=%s object_id=%s",
                    obj.storage_path,
                    obj.id,
                )
            else:
                logger.warning(
                    "Missing blob file for expired object path=%s object_id=%s",
                    obj.storage_path,
                    obj.id,
                )
        except ValueError:
            logger.warning("Unsafe storage_path skipped object_id=%s", obj.id)
        session.delete(obj)
        deleted += 1
    if deleted:
        session.commit()
    return deleted
