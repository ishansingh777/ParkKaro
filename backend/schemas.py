from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ParkingSpotOut(BaseModel):
    id: int
    name: str
    city: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    total_car_slots: int = 0
    total_bike_slots: int = 0
    available_car_slots: int = 0
    available_bike_slots: int = 0
    is_paid: bool = False
    price_per_hour: int = 0
    rule_type: str = "ALLOWED"
    rule_description: Optional[str] = None
    distance_km: Optional[float] = None
    earliest_free_time: Optional[str] = None

    class Config:
        from_attributes = True


class ParkingSpotCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=50)
    address: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    total_car_slots: int = Field(10, ge=0)
    total_bike_slots: int = Field(20, ge=0)
    is_paid: bool = False
    price_per_hour: int = Field(0, ge=0)
    rule_type: str = Field("ALLOWED", pattern="^(PAID|ALLOWED|NO_PARKING)$")
    rule_description: Optional[str] = None


class StatsResponse(BaseModel):
    total_spots: int
    available_car_slots: int
    available_bike_slots: int
    total_car_slots: int
    total_bike_slots: int
    active_bookings: int
    cities_count: int



class BookingCreate(BaseModel):
    spot_id: int
    user_name: str = Field(..., min_length=2, max_length=50)
    vehicle_type: str = Field("car", pattern="^(car|bike)$")
    duration_hours: int = Field(1, ge=1, le=24)


class BookingOut(BaseModel):
    id: int
    spot_id: int
    spot_name: Optional[str] = None
    city: Optional[str] = None
    user_name: str
    vehicle_type: str
    start_time: datetime
    end_time: datetime
    status: str
    is_checked_in: bool = False
    duration_hours: Optional[int] = None
    total_cost: Optional[int] = None

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CheckInResponse(BaseModel):
    booking_id: int
    status: str
    is_checked_in: bool
    message: str


class RushPredictionOut(BaseModel):
    spot_id: int
    hour: int
    day_of_week: int
    chance_of_full: str
    status: str


class HealthResponse(BaseModel):
    status: str
    database: str
    total_spots: int
    active_bookings: int
    models_loaded: dict
    timestamp: datetime
