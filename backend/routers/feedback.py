from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import quote

from database import get_db
from db_models import FeedbackSubmission
from schemas import FeedbackCreate, FeedbackOut

TARGET_FEEDBACK_EMAIL = "parkkaro99@gmail.com"

router = APIRouter(tags=["feedback"])


def build_gmail_compose_url(subject: str, body: str, sender_email: Optional[str] = None) -> str:
    """Build a direct Gmail web compose URL pre-addressed to parkkaro99@gmail.com."""
    full_body = body.strip()
    if sender_email:
        full_body = f"From: {sender_email.strip()}\n\n{full_body}"
    return (
        f"https://mail.google.com/mail/?view=cm&fs=1"
        f"&to={quote(TARGET_FEEDBACK_EMAIL)}"
        f"&su={quote(subject.strip() or 'ParkKaro App Feedback')}"
        f"&body={quote(full_body)}"
    )


def _to_feedback_out(row: FeedbackSubmission) -> FeedbackOut:
    return FeedbackOut(
        id=row.id,
        subject=row.subject,
        message=row.message,
        sender_email=row.sender_email,
        source_page=row.source_page or "home",
        status="saved",
        target_email=TARGET_FEEDBACK_EMAIL,
        gmail_compose_url=build_gmail_compose_url(row.subject, row.message, row.sender_email),
        created_at=row.created_at,
    )


@router.post("/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    """Save user feedback into Supabase PostgreSQL and return a Gmail compose fallback link."""
    clean_message = payload.message.strip()
    if not clean_message:
        raise HTTPException(status_code=400, detail="Please enter your feedback message before submitting.")

    clean_subject = payload.subject.strip() or "ParkKaro App Feedback"
    clean_sender = payload.sender_email.strip() if payload.sender_email else None
    if clean_sender == "":
        clean_sender = None

    entry = FeedbackSubmission(
        subject=clean_subject,
        message=clean_message,
        sender_email=clean_sender,
        source_page=(payload.source_page or "home").strip() or "home",
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_feedback_out(entry)


@router.get("/feedback", response_model=List[FeedbackOut])
def list_feedback(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """List recent saved user feedback submissions ordered newest first."""
    rows = (
        db.query(FeedbackSubmission)
        .order_by(FeedbackSubmission.created_at.desc(), FeedbackSubmission.id.desc())
        .limit(limit)
        .all()
    )
    return [_to_feedback_out(r) for r in rows]
