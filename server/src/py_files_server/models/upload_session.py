"""Resumable upload session entity."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from py_files_server.models.base import Base


class UploadSessionState(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(1024), nullable=False)
    expected_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    received_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    partial_storage_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    state: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=UploadSessionState.ACTIVE.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    owner: Mapped["User"] = relationship("User", back_populates="upload_sessions")


from typing import TYPE_CHECKING  # noqa: E402

if TYPE_CHECKING:
    from py_files_server.models.user import User
