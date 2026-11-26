"""Supabase-backed request logs, latency telemetry, and developer audit logging."""

import time
from typing import Any, Dict, List, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from db_models import AuditLog, ServerLog, User

APP_START_TIME = time.time()


def extract_client_ip(request: Request) -> str:
    """Extract requester IP cleanly without trusting malformed headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    if request.client and request.client.host:
        return request.client.host[:64]
    return "unknown"


def persist_server_log(
    db: Session,
    *,
    level: str,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    ip_address: str,
    user_id: Optional[int] = None,
    user_role: Optional[str] = None,
    message: Optional[str] = None,
) -> None:
    """Persist API request/error telemetry directly into Supabase server_logs."""
    try:
        log_row = ServerLog(
            level=level,
            method=method[:12],
            path=path[:255],
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address[:64] if ip_address else None,
            message=message[:1000] if message else None,
        )
        db.add(log_row)
        db.commit()
    except Exception:
        db.rollback()


def record_audit_action(
    db: Session,
    *,
    actor: User,
    action: str,
    ip_address: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    """Persist an immutable developer/privilege audit log row in Supabase."""
    entry = AuditLog(
        actor_user_id=actor.id,
        actor_email=actor.email,
        action=action[:100],
        target_type=target_type[:64] if target_type else None,
        target_id=str(target_id)[:64] if target_id is not None else None,
        ip_address=ip_address[:64] if ip_address else None,
        details=details[:2000] if details else None,
    )
    db.add(entry)
    db.commit()


def get_recent_server_logs(db: Session, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query recent request & error logs from Supabase PostgreSQL."""
    query = db.query(ServerLog)
    if level and level.upper() in {"INFO", "WARN", "ERROR"}:
        query = query.filter(ServerLog.level == level.upper())
    rows = query.order_by(ServerLog.id.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "level": r.level,
            "method": r.method,
            "path": r.path,
            "status_code": r.status_code,
            "duration_ms": round(float(r.duration_ms or 0.0), 2),
            "user_id": r.user_id,
            "user_role": r.user_role,
            "ip_address": r.ip_address,
            "message": r.message,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


def get_latency_summary(db: Session) -> Dict[str, Any]:
    """Compute average, p95 response times, and error count from Supabase server_logs."""
    rows = db.query(ServerLog.duration_ms, ServerLog.status_code).order_by(ServerLog.id.desc()).limit(250).all()
    if not rows:
        return {"sample_size": 0, "avg_ms": 0.0, "p95_ms": 0.0, "error_count": 0}
    durations = sorted(float(r.duration_ms or 0.0) for r in rows)
    idx_95 = min(len(durations) - 1, int(0.95 * (len(durations) - 1)))
    errors = sum(1 for r in rows if (r.status_code or 0) >= 500)
    return {
        "sample_size": len(rows),
        "avg_ms": round(sum(durations) / len(durations), 2),
        "p95_ms": round(durations[idx_95], 2),
        "error_count": errors,
    }
