from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=True)
    phone_number = Column(String(30), unique=True, index=True, nullable=True)
    vehicle_number = Column(String(30), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(10), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
