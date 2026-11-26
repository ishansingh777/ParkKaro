"""Developer-only observability, database diagnostics, logs, and user management."""

from datetime import datetime, timezone
import os
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
try:
    import psutil
except ImportError:
    psutil = None
from sqlalchemy import text
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from auth.logging_utils import (
    APP_START_TIME,
    extract_client_ip,
    get_latency_summary,
    get_recent_server_logs,
    record_audit_action,
)
from database import engine, get_db
from db_models import ActiveBooking, AuditLog, FeedbackSubmission, ParkingSpot, ServerLog, User
from schemas import AuthUserOut, UserStatusUpdate

router = APIRouter(
    prefix="/dev",
    tags=["developer"],
    dependencies=[Depends(require_role("developer"))],
)


@router.get("/db-status")
def dev_db_status(
    request: Request,
    current_dev: User = Depends(require_role("developer")),
    db: Session = Depends(get_db),
):
    """Return Supabase PostgreSQL health, size, active sessions, and table counts."""
    dialect_name = db.bind.dialect.name if db.bind else "unknown"
    db_version = "unknown"
    db_name = "unknown"
    db_size_bytes = None
    active_connections = None

    try:
        if dialect_name == "postgresql":
            row = db.execute(
                text(
                    "SELECT version(), current_database(), pg_database_size(current_database())"
                )
            ).fetchone()
            if row:
                db_version = str(row[0]).split(",")[0]
                db_name = str(row[1])
                db_size_bytes = int(row[2]) if row[2] is not None else None
            conn_row = db.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
            ).fetchone()
            if conn_row:
                active_connections = int(conn_row[0])
        else:
            row = db.execute(text("SELECT sqlite_version()")).fetchone()
            db_version = f"SQLite {row[0]}" if row else dialect_name
            db_name = dialect_name
    except Exception as exc:
        db.rollback()
        db_version = f"{dialect_name} (diagnostics limited: {type(exc).__name__})"

    counts = {
        "users": db.query(User).count(),
        "developers": db.query(User).filter(User.role == "developer").count(),
        "parking_spots": db.query(ParkingSpot).count(),
        "active_bookings": db.query(ActiveBooking).filter(ActiveBooking.status == "active").count(),
        "total_bookings": db.query(ActiveBooking).count(),
        "feedback_submissions": db.query(FeedbackSubmission).count(),
        "audit_logs": db.query(AuditLog).count(),
        "server_logs": db.query(ServerLog).count(),
    }

    pool = engine.pool
    pool_info = {
        "pool_class": type(pool).__name__,
        "size": pool.size() if hasattr(pool, "size") else None,
        "checked_in": pool.checkedin() if hasattr(pool, "checkedin") else None,
        "checked_out": pool.checkedout() if hasattr(pool, "checkedout") else None,
    }

    record_audit_action(
        db,
        actor=current_dev,
        action="VIEW_DB_STATUS",
        ip_address=extract_client_ip(request),
        target_type="database",
        details="Inspected database health and table metrics",
    )

    return {
        "status": "connected",
        "dialect": dialect_name,
        "database_name": db_name,
        "version": db_version,
        "size_mb": round(db_size_bytes / (1024 * 1024), 2) if db_size_bytes is not None else None,
        "active_connections": active_connections,
        "pool": pool_info,
        "table_counts": counts,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health")
def dev_server_health(
    request: Request,
    current_dev: User = Depends(require_role("developer")),
    db: Session = Depends(get_db),
):
    """Return server CPU, memory, uptime, ML model state, and API latency stats."""
    if psutil:
        proc = psutil.Process(os.getpid())
        mem_info = proc.memory_info()
        vm = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.05)
        proc_mem = round(mem_info.rss / (1024 * 1024), 2)
        sys_mem_percent = vm.percent
        sys_mem_total = round(vm.total / (1024 ** 3), 2)
    else:
        cpu_percent = 0.0
        proc_mem = 0.0
        sys_mem_percent = 0.0
        sys_mem_total = 0.0

    loaded_models = getattr(request.app.state, "models", {}) or {}
    uptime_seconds = round(time.time() - APP_START_TIME, 1)

    record_audit_action(
        db,
        actor=current_dev,
        action="VIEW_SERVER_HEALTH",
        ip_address=extract_client_ip(request),
        target_type="server",
    )

    return {
        "status": "ok",
        "uptime_seconds": uptime_seconds,
        "cpu_percent": cpu_percent,
        "process_memory_mb": proc_mem,
        "system_memory_percent": sys_mem_percent,
        "system_memory_total_gb": sys_mem_total,
        "models_loaded": {k: (v is not None) for k, v in loaded_models.items()},
        "api_latency": get_latency_summary(db),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/logs")
def dev_server_logs(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None, description="Filter by INFO, WARN, or ERROR"),
    current_dev: User = Depends(require_role("developer")),
    db: Session = Depends(get_db),
):
    """Return Supabase-backed request/error logs and recent audit log entries."""
    logs = get_recent_server_logs(db, limit=limit, level=level)
    audit_rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()

    record_audit_action(
        db,
        actor=current_dev,
        action="VIEW_LOGS",
        ip_address=extract_client_ip(request),
        target_type="server_logs",
        details=f"limit={limit}, level={level or 'ALL'}",
    )

    return {
        "request_logs": logs,
        "audit_logs": [
            {
                "id": a.id,
                "actor_user_id": a.actor_user_id,
                "actor_email": a.actor_email,
                "action": a.action,
                "target_type": a.target_type,
                "target_id": a.target_id,
                "ip_address": a.ip_address,
                "details": a.details,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in audit_rows
        ],
    }


@router.get("/users")
def dev_list_users(
    request: Request,
    current_dev: User = Depends(require_role("developer")),
    db: Session = Depends(get_db),
):
    """List all registered users (strictly omitting password hashes)."""
    users = db.query(User).order_by(User.id.asc()).all()

    record_audit_action(
        db,
        actor=current_dev,
        action="VIEW_USERS",
        ip_address=extract_client_ip(request),
        target_type="users",
        details=f"Listed {len(users)} users",
    )

    return {
        "total": len(users),
        "users": [AuthUserOut.model_validate(u) for u in users],
    }


@router.patch("/users/{user_id}/status", response_model=AuthUserOut)
def dev_toggle_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    request: Request,
    current_dev: User = Depends(require_role("developer")),
    db: Session = Depends(get_db),
):
    """Enable or disable a user account and write an audit log entry."""
    if user_id == current_dev.id and not payload.is_active:
        raise HTTPException(
            status_code=400,
            detail="Developers cannot deactivate their own active account.",
        )

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    previous_state = target.is_active
    target.is_active = payload.is_active
    db.commit()
    db.refresh(target)

    record_audit_action(
        db,
        actor=current_dev,
        action="UPDATE_USER_STATUS",
        ip_address=extract_client_ip(request),
        target_type="user",
        target_id=str(target.id),
        details=f"email={target.email} is_active: {previous_state} -> {target.is_active}",
    )

    return target
