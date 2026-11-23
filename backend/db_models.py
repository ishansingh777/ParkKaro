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
