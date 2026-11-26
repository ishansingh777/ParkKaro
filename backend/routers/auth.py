import os
import hashlib
import secrets
import base64
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from db_models import User
from schemas import UserSignUp, UserVerify, UserLogin, UserOut, AuthResponse

router = APIRouter(tags=["auth"])

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "parkkaro-secure-salt-key-2026")


def hash_password(password: str) -> str:
    """Secure PBKDF2-HMAC-SHA256 hashing with unique salt."""
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 100000)
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed: str) -> bool:
    """Verify password against stored salt and PBKDF2 key."""
    try:
        salt, key_hex = hashed.split("$")
        key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), bytes.fromhex(salt), 100000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


def generate_token(user: User) -> str:
    """Generate tamper-resistant session token."""
    payload = {
        "uid": user.id,
        "email": user.email,
        "is_verified": user.is_verified,
        "ts": int(datetime.now(timezone.utc).timestamp())
    }
    payload_str = json.dumps(payload, separators=(',', ':'))
    sig = hashlib.sha256(f"{payload_str}:{SECRET_KEY}".encode()).hexdigest()[:16]
    token_bytes = f"{payload_str}::{sig}".encode()
    return base64.urlsafe_b64encode(token_bytes).decode()


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify signature of token."""
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        payload_str, sig = raw.split("::")
        expected_sig = hashlib.sha256(f"{payload_str}:{SECRET_KEY}".encode()).hexdigest()[:16]
        if secrets.compare_digest(sig, expected_sig):
            return json.loads(payload_str)
    except Exception:
        pass
    return None


@router.post("/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(data: UserSignUp, db: Session = Depends(get_db)):
    """
    Register a new user in Supabase with phone, vehicle number, and 6-digit verification code.
    New users start as is_verified=False until they verify their 6-digit code.
    """
    clean_email = data.email.strip().lower()
    clean_phone = data.phone_number.strip() if data.phone_number else None
    clean_vehicle = data.vehicle_number.strip().upper() if data.vehicle_number else None

    # Check for existing email or phone
    existing_user = db.query(User).filter(
        or_(
            User.email == clean_email,
            (User.phone_number == clean_phone) if clean_phone else False
        )
    ).first()

    if existing_user:
        if existing_user.email == clean_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists. Please log in or use another email."
            )
        if clean_phone and existing_user.phone_number == clean_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this phone number already exists."
            )

    # Generate 6-digit OTP code (e.g. 749201)
    otp_code = str(100000 + secrets.randbelow(900000))
    pwd_hash = hash_password(data.password)

    new_user = User(
        email=clean_email,
        full_name=data.full_name.strip(),
        phone_number=clean_phone,
        vehicle_number=clean_vehicle,
        password_hash=pwd_hash,
        role="user",
        is_active=True,
        is_verified=False,
        verification_code=otp_code
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during registration: {str(e)}")

    user_out = UserOut.from_orm(new_user)
    return AuthResponse(
        status="verification_required",
        message="Account created successfully in Supabase! Please enter your 6-digit verification code to activate your account.",
        is_verified=False,
        user=user_out,
        verification_code_hint=otp_code
    )


@router.post("/auth/verify", response_model=AuthResponse)
def verify_account(data: UserVerify, db: Session = Depends(get_db)):
    """
    Verify a user account using their 6-digit code.
    Once verified, updates Supabase record and unlocks full booking access.
    """
    clean_email = data.email.strip().lower()
    code = data.verification_code.strip()

    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found with this email.")

    if user.is_verified:
        token = generate_token(user)
        return AuthResponse(
            status="already_verified",
            message="Your account is already verified! You can proceed to book parking slots.",
            is_verified=True,
            user=UserOut.from_orm(user),
            token=token
        )

    if not user.verification_code or user.verification_code.strip() != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please check and enter the correct 6-digit code."
        )

    # Mark user verified in Supabase
    user.is_verified = True
    user.verification_code = None
    user.verified_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update verification status: {str(e)}")

    token = generate_token(user)
    return AuthResponse(
        status="verified",
        message="🎉 Account verified successfully! You are now authorized to book live parking spots.",
        is_verified=True,
        user=UserOut.from_orm(user),
        token=token
    )


@router.post("/auth/login", response_model=AuthResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Sign in with email or phone number.
    Strictly verifies that user is verified before granting active access.
    """
    identifier = data.email_or_phone.strip().lower()

    user = db.query(User).filter(
        or_(
            User.email == identifier,
            User.phone_number == data.email_or_phone.strip()
        )
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password. Please try again."
        )

    # Enforce verification check
    if not user.is_verified:
        # If no code exists, generate a fresh one
        if not user.verification_code:
            user.verification_code = str(100000 + secrets.randbelow(900000))
            db.commit()

        return AuthResponse(
            status="unverified",
            message="Your account is not verified yet. Please enter your verification code to continue.",
            is_verified=False,
            user=UserOut.from_orm(user),
            verification_code_hint=user.verification_code
        )

    token = generate_token(user)
    return AuthResponse(
        status="authenticated",
        message="Welcome back to ParkKaro! Verified driver session active.",
        is_verified=True,
        user=UserOut.from_orm(user),
        token=token
    )


@router.get("/auth/me", response_model=UserOut)
def get_current_user(
    authorization: Optional[str] = Header(None),
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get profile of currently logged-in verified user.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        decoded = decode_token(token)
        if decoded:
            user = db.query(User).filter(User.id == decoded["uid"]).first()
            if user:
                return UserOut.from_orm(user)

    if email:
        user = db.query(User).filter(User.email == email.strip().lower()).first()
        if user:
            return UserOut.from_orm(user)

    raise HTTPException(status_code=401, detail="Not authenticated or invalid token")
