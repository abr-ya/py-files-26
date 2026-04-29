"""Password hashing with bcrypt."""

from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash password for storage."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, password_hash: str) -> bool:
    """Verify plaintext password against stored hash."""
    return _pwd_context.verify(plain, password_hash)
