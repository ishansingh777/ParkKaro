"""One-time safe seed script to create or promote ONE specific email to developer.

Usage:
    python scripts/seed_developer.py --email you@example.com
Or via environment variables:
    DEV_SEED_EMAIL=you@example.com DEV_SEED_PASSWORD='...' python scripts/seed_developer.py
"""

import argparse
import getpass
import os
import sys

# Allow running directly from ParkKaro/backend or repo root
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException  # noqa: E402
from auth.security import hash_password, normalize_email, validate_email_format, validate_password_strength  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
from db_models import User  # noqa: E402


def seed_developer(email: str, password: str, full_name: str = "Developer Admin", db_session=None) -> User:
    """Create or promote exactly one specific email to role='developer' safely."""
    clean_email = validate_email_format(email)
    validate_password_strength(password, min_length=10)

    owns_session = db_session is None
    db = db_session or SessionLocal()
    try:
        if owns_session:
            Base.metadata.create_all(bind=engine, checkfirst=True)

        user = db.query(User).filter(User.email == clean_email).first()
        pw_hash = hash_password(password)
        if user:
            user.role = "developer"
            user.is_active = True
            user.password_hash = pw_hash
            if full_name and not user.full_name:
                user.full_name = full_name
        else:
            user = User(
                email=clean_email,
                full_name=full_name,
                password_hash=pw_hash,
                role="developer",
                is_active=True,
            )
            db.add(user)

        db.commit()
        db.refresh(user)
        return user
    finally:
        if owns_session:
            db.close()


def main():
    parser = argparse.ArgumentParser(description="Safely seed/promote one developer account.")
    parser.add_argument("--email", default=os.getenv("DEV_SEED_EMAIL", ""), help="Developer email address")
    parser.add_argument("--name", default=os.getenv("DEV_SEED_NAME", "ParkKaro Developer"), help="Display name")
    args = parser.parse_args()

    email = normalize_email(args.email)
    if not email:
        email = input("Developer email: ").strip().lower()

    password = os.getenv("DEV_SEED_PASSWORD", "")
    if not password:
        password = getpass.getpass("Strong developer password (min 10 chars, letters + digits): ")

    try:
        user = seed_developer(email=email, password=password, full_name=args.name)
        print(f"Developer account ready: id={user.id}, email={user.email}, role={user.role}")
    except HTTPException as exc:
        print(f"Validation failed: {exc.detail}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
