"""Authentication routes: public user-only signup, login, logout, and session probe."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from auth.dependencies import auth
from auth.logging_utils import extract_client_ip
from auth.security import (
    check_login_rate_limit,
    clear_auth_cookie,
    clear_login_failures,
    create_access_token,
    dummy_password_check,
    hash_password,
    record_failed_login,
    set_auth_cookie,
    validate_email_format,
    validate_password_strength,
    verify_password,
)
from database import get_db
from db_models import User
from schemas import AuthUserOut, LoginRequest, SignupRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthUserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    """Register a standard user account. Client-supplied roles are always ignored."""
    email = validate_email_format(payload.email)
    validate_password_strength(payload.password, min_length=8)

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    clean_name = payload.full_name.strip() if payload.full_name else None
    if clean_name == "":
        clean_name = None

    new_user = User(
        email=email,
        full_name=clean_name,
        password_hash=hash_password(payload.password),
        role="user",  # Never allow signup to escalate privileges
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(user_id=new_user.id, role=new_user.role)
    set_auth_cookie(response, token)
    request.state.auth_user_id = new_user.id
    request.state.auth_user_role = new_user.role
    return new_user


@router.post("/login", response_model=AuthUserOut)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    """Verify credentials against Supabase, enforce rate limit, and issue HttpOnly JWT cookie."""
    email = validate_email_format(payload.email)
    client_ip = extract_client_ip(request)

    check_login_rate_limit(db, client_ip, email)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        dummy_password_check(payload.password)
        record_failed_login(db, client_ip, email)
        request.state.log_message = "Failed login attempt (unknown email)"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    password_ok = verify_password(payload.password, user.password_hash)
    if not password_ok or not user.is_active:
        record_failed_login(db, client_ip, email)
        request.state.auth_user_id = user.id
        request.state.auth_user_role = user.role
        request.state.log_message = "Failed login attempt (invalid password or disabled account)"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    clear_login_failures(db, client_ip, email)
    token = create_access_token(user_id=user.id, role=user.role)
    set_auth_cookie(response, token)
    request.state.auth_user_id = user.id
    request.state.auth_user_role = user.role
    return user


@router.post("/logout")
def logout(response: Response):
    """Clear the HttpOnly session cookie."""
    clear_auth_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AuthUserOut)
def get_me(current_user: User = Depends(auth)):
    """Return the authenticated user's profile and DB-authoritative role."""
    return current_user
