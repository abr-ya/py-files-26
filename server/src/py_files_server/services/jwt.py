"""JWT access tokens (HS256)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt

from py_files_server.settings import Settings


def create_access_token(subject_user_id: uuid.UUID, settings: Settings) -> str:
    """Issue JWT access token with ``sub`` = user UUID."""
    now = datetime.now(tz=UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(subject_user_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token_payload(token: str, settings: Settings) -> dict:
    """Decode and validate JWT payload or raise HTTP 401."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def parse_subject_uuid(payload: dict) -> uuid.UUID:
    """Extract ``sub`` claim as UUID."""
    raw = payload.get("sub")
    if raw is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    try:
        return uuid.UUID(str(raw))
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject") from exc
