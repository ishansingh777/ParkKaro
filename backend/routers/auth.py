"""Authentication routes: verified driver registration, 6-digit OTP verification, RBAC login, and session probe."""

import secrets
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import or_
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
from schemas import AuthResponse, LoginRequest, SignupRequest, UserOut, UserVerify
from services.email_service import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Register a user account in Supabase.
    If phone number or vehicle number is provided, sets is_verified=False and issues
    a 6-digit verification code. Client-supplied role is always restricted to 'user'.
    """
    clean_email = validate_email_format(payload.email)
    validate_password_strength(payload.password, min_length=8)

    clean_phone = payload.phone_number.strip() if payload.phone_number else None
    clean_vehicle = payload.vehicle_number.strip().upper() if payload.vehicle_number else None
    clean_name = payload.full_name.strip() if payload.full_name else None
    if clean_name == "":
        clean_name = None

    existing = db.query(User).filter(
        or_(
            User.email == clean_email,
            (User.phone_number == clean_phone) if clean_phone else False
        )
    ).first()

    if existing:
        if existing.email == clean_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )
        if clean_phone and existing.phone_number == clean_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this phone number already exists.",
            )

    # If phone or vehicle is supplied, require 6-digit verification code
    requires_verification = bool(clean_phone or clean_vehicle)
    otp_code = str(100000 + secrets.randbelow(900000)) if requires_verification else None
    pwd_hash = hash_password(payload.password)

    new_user = User(
        email=clean_email,
        full_name=clean_name,
        phone_number=clean_phone,
        vehicle_number=clean_vehicle,
        password_hash=pwd_hash,
        role="user",  # Never allow signup to escalate privileges
        is_active=True,
        is_verified=not requires_verification,
        verification_code=otp_code,
        verified_at=datetime.now(timezone.utc) if not requires_verification else None,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during registration: {str(exc)}",
        )

    token = create_access_token(user_id=new_user.id, role=new_user.role)
    set_auth_cookie(response, token)
    request.state.auth_user_id = new_user.id
    request.state.auth_user_role = new_user.role

    # Send verification email if OTP code generated
    if otp_code:
        send_verification_email(new_user.email, otp_code, new_user.full_name)

    user_out = UserOut.from_orm(new_user)
    status_str = "verification_required" if requires_verification else "success"
    message_str = (
        "Account created successfully in Supabase! Please enter your 6-digit verification code to activate your account."
        if requires_verification
        else "Account created successfully!"
    )

    return AuthResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        phone_number=new_user.phone_number,
        vehicle_number=new_user.vehicle_number,
        role=new_user.role,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        created_at=new_user.created_at,
        status=status_str,
        message=message_str,
        user=user_out,
        token=token,
        verification_code_hint=otp_code,
    )


@router.post("/verify", response_model=AuthResponse)
def verify_account(data: UserVerify, response: Response, db: Session = Depends(get_db)):
    """
    Verify a user account using their 6-digit code.
    Once verified, updates Supabase record and unlocks full booking access.
    """
    clean_email = data.email.strip().lower()
    code = data.verification_code.strip()

    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found with this email.",
        )

    if user.is_verified:
        token = create_access_token(user_id=user.id, role=user.role)
        set_auth_cookie(response, token)
        return AuthResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            vehicle_number=user.vehicle_number,
            role=user.role,
            is_active=user.is_active,
            is_verified=True,
            created_at=user.created_at,
            status="already_verified",
            message="Your account is already verified! You can proceed to book parking slots.",
            user=UserOut.from_orm(user),
            token=token,
        )

    if not user.verification_code or user.verification_code.strip() != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please check and enter the correct 6-digit code.",
        )

    user.is_verified = True
    user.verification_code = None
    user.verified_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(user)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update verification status: {str(exc)}",
        )

    token = create_access_token(user_id=user.id, role=user.role)
    set_auth_cookie(response, token)

    return AuthResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        vehicle_number=user.vehicle_number,
        role=user.role,
        is_active=user.is_active,
        is_verified=True,
        created_at=user.created_at,
        status="verified",
        message="🎉 Account verified successfully! You are now authorized to book live parking spots.",
        user=UserOut.from_orm(user),
        token=token,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    """Verify credentials against Supabase, enforce rate limit, and issue HttpOnly JWT cookie."""
    raw_ident = payload.email_or_phone or payload.email or ""
    clean_ident = raw_ident.strip().lower()
    client_ip = extract_client_ip(request)

    check_login_rate_limit(db, client_ip, clean_ident)

    user = db.query(User).filter(
        or_(
            User.email == clean_ident,
            User.phone_number == raw_ident.strip()
        )
    ).first()

    if not user:
        dummy_password_check(payload.password)
        record_failed_login(db, client_ip, clean_ident)
        request.state.log_message = "Failed login attempt (unknown email)"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    password_ok = verify_password(payload.password, user.password_hash)
    if not password_ok or not user.is_active:
        record_failed_login(db, client_ip, clean_ident)
        request.state.auth_user_id = user.id
        request.state.auth_user_role = user.role
        request.state.log_message = "Failed login attempt (invalid password or disabled account)"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Check verification status (developer role is automatically verified)
    if user.role == "developer":
        user.is_verified = True

    if not user.is_verified:
        if not user.verification_code:
            user.verification_code = str(100000 + secrets.randbelow(900000))
            db.commit()

        # Send fresh verification email
        send_verification_email(user.email, user.verification_code, user.full_name)

        return AuthResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            vehicle_number=user.vehicle_number,
            role=user.role,
            is_active=user.is_active,
            is_verified=False,
            created_at=user.created_at,
            status="unverified",
            message="Your account is not verified yet. Please enter your verification code to continue.",
            user=UserOut.from_orm(user),
            verification_code_hint=user.verification_code,
        )

    clear_login_failures(db, client_ip, clean_ident)
    token = create_access_token(user_id=user.id, role=user.role)
    set_auth_cookie(response, token)
    request.state.auth_user_id = user.id
    request.state.auth_user_role = user.role

    return AuthResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        vehicle_number=user.vehicle_number,
        role=user.role,
        is_active=user.is_active,
        is_verified=True,
        created_at=user.created_at,
        status="authenticated",
        message="Welcome back to ParkKaro! Verified driver session active.",
        user=UserOut.from_orm(user),
        token=token,
    )


@router.post("/logout")
def logout(response: Response):
    """Clear the HttpOnly session cookie."""
    clear_auth_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AuthResponse)
def get_me(current_user: User = Depends(auth)):
    """Return the authenticated user's profile and DB-authoritative role."""
    return AuthResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        vehicle_number=current_user.vehicle_number,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        status="authenticated",
        user=UserOut.from_orm(current_user),
    )
