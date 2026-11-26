"""Password hashing, JWT session cookies, and Supabase-backed login rate limiting."""

from datetime import datetime, timedelta, timezone
import re

import bcrypt
import jwt
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from config import settings
from db_models import LoginAttempt

# Precomputed valid bcrypt hash used to normalize timing when an email is unknown.
_DUMMY_BCRYPT_HASH = bcrypt.hashpw(b"parkkaro-timing-equalizer-password", bcrypt.gensalt()).decode("utf-8")
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def normalize_email(email: str) -> str:
    """Normalize and trim email addresses consistently."""
    return (email or "").strip().lower()


def validate_email_format(email: str) -> str:
    """Validate normalized email format or raise 422."""
    cleaned = normalize_email(email)
    if not cleaned or len(cleaned) > 254 or not _EMAIL_RE.match(cleaned):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please provide a valid email address.",
        )
    return cleaned


def validate_password_strength(password: str, min_length: int = 8) -> str:
    """Validate minimum password complexity rules."""
    if not password or len(password) < min_length or len(password) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be between {min_length} and 128 characters.",
        )
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must include both letters and numbers.",
        )
    return password


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Constant-time bcrypt comparison against stored password hash."""
    if not plain_password or not password_hash:
        bcrypt.checkpw(b"invalid", _DUMMY_BCRYPT_HASH.encode("utf-8"))
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def dummy_password_check(plain_password: str) -> None:
    """Spend equal bcrypt work when a login email does not exist."""
    try:
        bcrypt.checkpw((plain_password or "").encode("utf-8"), _DUMMY_BCRYPT_HASH.encode("utf-8"))
    except ValueError:
        pass


def _require_jwt_secret() -> str:
    secret = (settings.jwt_secret or "").strip()
    if not secret:
        raise RuntimeError("JWT_SECRET environment variable must be set in backend/.env")
    return secret


def create_access_token(user_id: int, role: str) -> str:
    """Issue a signed short-lived JWT containing user ID and role."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, _require_jwt_secret(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Verify JWT signature and expiration; raise ValueError on any failure."""
    try:
        return jwt.decode(
            token,
            _require_jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "role", "exp", "iat"]},
        )
    except (jwt.PyJWTError, RuntimeError) as exc:
        raise ValueError("Invalid or expired session token") from exc


def set_auth_cookie(response: Response, token: str) -> None:
    """Attach the session token strictly as an HttpOnly, SameSite, Secure cookie."""
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """Clear the authentication cookie on logout."""
    response.delete_cookie(
        key=settings.cookie_name,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


def check_login_rate_limit(db: Session, ip_address: str, email: str) -> None:
    """Enforce login rate limits stored directly in Supabase PostgreSQL."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=settings.login_rate_limit_window_sec)
    ip_key = (ip_address or "unknown")[:64]
    email_key = normalize_email(email)[:254]

    # Opportunistic cleanup of expired attempts older than 2 windows
    stale_cutoff = now - timedelta(seconds=settings.login_rate_limit_window_sec * 2)
    db.query(LoginAttempt).filter(LoginAttempt.created_at < stale_cutoff).delete(synchronize_session=False)
    db.commit()

    pair_count = db.query(LoginAttempt).filter(
        LoginAttempt.ip_address == ip_key,
        LoginAttempt.email == email_key,
        LoginAttempt.created_at >= window_start,
    ).count()
    ip_count = db.query(LoginAttempt).filter(
        LoginAttempt.ip_address == ip_key,
        LoginAttempt.created_at >= window_start,
    ).count()

    if pair_count >= settings.login_rate_limit_max or ip_count >= (settings.login_rate_limit_max * 3):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait a minute before trying again.",
        )


def record_failed_login(db: Session, ip_address: str, email: str) -> None:
    """Persist a failed login attempt into Supabase PostgreSQL."""
    entry = LoginAttempt(
        ip_address=(ip_address or "unknown")[:64],
        email=normalize_email(email)[:254],
    )
    db.add(entry)
    db.commit()


def clear_login_failures(db: Session, ip_address: str, email: str) -> None:
    """Clear failed login attempts for this IP+email after successful auth."""
    ip_key = (ip_address or "unknown")[:64]
    email_key = normalize_email(email)[:254]
    db.query(LoginAttempt).filter(
        LoginAttempt.ip_address == ip_key,
        LoginAttempt.email == email_key,
    ).delete(synchronize_session=False)
    db.commit()
