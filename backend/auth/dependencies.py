"""FastAPI authentication and role-based access control dependencies."""

from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from auth.security import decode_access_token
from config import settings
from database import get_db
from db_models import User


def _resolve_user_from_cookie(request: Request, db: Session) -> Optional[User]:
    token = request.cookies.get(settings.cookie_name)
    if not token:
        # Fallback to Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (ValueError, KeyError, TypeError):
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None

    request.state.auth_user_id = user.id
    request.state.auth_user_role = user.role
    return user


def auth(request: Request, db: Session = Depends(get_db)) -> User:
    """Require a valid HttpOnly JWT cookie or Bearer token backed by an active database user."""
    user = _resolve_user_from_cookie(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return user


# Descriptive alias used alongside `auth`
get_current_user = auth


def optional_auth(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Return the authenticated user if a valid cookie or token is present, else None."""
    return _resolve_user_from_cookie(request, db)


def require_role(*roles: str) -> Callable[[User], User]:
    """Enforce that the database-backed user holds one of the allowed roles."""
    allowed = set(roles)

    def role_checker(current_user: User = Depends(auth)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return role_checker
