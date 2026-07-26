"""Schemas for resumable upload sessions."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class UploadSessionCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=1024)
    total_size: int = Field(ge=0)
    sha256: str | None = Field(default=None, min_length=64, max_length=64)


class UploadSessionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    received_bytes: int
    expected_size: int
    state: str


class OffsetMismatch(BaseModel):
    expected_offset: int

