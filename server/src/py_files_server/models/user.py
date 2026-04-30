"""User entity."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from py_files_server.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    external_google_sub: Mapped[str | None] = mapped_column(String(255), nullable=True)

    stored_objects: Mapped[list["StoredUploadObject"]] = relationship(
        "StoredUploadObject",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    upload_sessions: Mapped[list["UploadSession"]] = relationship(
        "UploadSession",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


from typing import TYPE_CHECKING  # noqa: E402

if TYPE_CHECKING:
    from py_files_server.models.stored_object import StoredUploadObject
    from py_files_server.models.upload_session import UploadSession
