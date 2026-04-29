"""Authentication routes (`/auth/register`, `/auth/login`)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from py_files_server.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from py_files_server.db import get_db
from py_files_server.models.user import User
from py_files_server.services.jwt import create_access_token
from py_files_server.services.password import hash_password, verify_password
from py_files_server.settings import Settings, get_settings

router = APIRouter(tags=["Auth"])


def _normalize_login(login: str) -> str:
    return login.strip().lower()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(
    body: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserPublic:
    """Create account when deployment policy allows self-registration (FR-010)."""
    if not settings.allow_self_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled on this server. Ask an administrator for an account.",
        )
    normalized = _normalize_login(body.login)
    existing = db.scalars(select(User).where(User.login == normalized)).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already taken")
    user = User(login=normalized, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserPublic(id=user.id, login=user.login)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Issue JWT access token."""
    normalized = _normalize_login(body.login)
    user = db.scalars(select(User).where(User.login == normalized)).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
        )
    token = create_access_token(user.id, settings)
    return TokenResponse(access_token=token)
