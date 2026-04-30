"""Schemas for resumable upload session API."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class UploadSessionCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=1024)
    total_size: int = Field(gt=0)


class UploadSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    received_bytes: int
    expected_size: int
