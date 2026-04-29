"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from py_files_server.db import get_db
from py_files_server.models.user import User
from py_files_server.services.jwt import decode_access_token_payload, parse_subject_uuid
from py_files_server.settings import Settings, get_settings

security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """Resolve Bearer JWT to persisted ``User``."""
    payload = decode_access_token_payload(credentials.credentials, settings)
    uid = parse_subject_uuid(payload)
    user = db.get(User, uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )
    return user
