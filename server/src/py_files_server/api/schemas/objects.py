"""Schemas for stored object responses."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StoredObjectMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    byte_size: int
    created_at: datetime
    expires_at: datetime
