from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, CheckConstraint
from sqlalchemy.sql import func
from database import Base

class User(Base):
    """Application user account with server-enforced RBAC role."""
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'developer')", name="ck_users_role"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=True)
    total_car_slots = Column(Integer, default=0)
    total_bike_slots = Column(Integer, default=0)
    is_paid = Column(Boolean, default=False)
    price_per_hour = Column(Integer, default=0)
    rule_type = Column(String, default="ALLOWED")
    rule_description = Column(String, nullable=True)
    external_spot_id = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ActiveBooking(Base):
    __tablename__ = "active_bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_name = Column(String, nullable=False)
    vehicle_type = Column(String, default="car")
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="active")
    is_checked_in = Column(Boolean, default=False)
    check_in_time = Column(DateTime(timezone=True), nullable=True)


class FeedbackSubmission(Base):
    __tablename__ = "feedback_submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject = Column(String(200), nullable=False)
    message = Column(String, nullable=False)
    sender_email = Column(String(120), nullable=True)
    source_page = Column(String(50), default="home")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """Persistent trail of developer actions and privilege-sensitive events."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    actor_email = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(64), nullable=True)
    target_id = Column(String(64), nullable=True)
    ip_address = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ServerLog(Base):
    """Persisted security/error log entries inspected on the developer dashboard."""
    __tablename__ = "server_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(String(16), nullable=False, default="INFO", index=True)
    method = Column(String(12), nullable=False)
    path = Column(String(255), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    duration_ms = Column(Float, nullable=False, default=0.0)
    user_id = Column(Integer, nullable=True)
    user_role = Column(String(32), nullable=True)
    ip_address = Column(String(64), nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class LoginAttempt(Base):
    """Supabase-persisted failed login timestamps for distributed rate limiting."""
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ip_address = Column(String(64), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
