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
    total_car_slots: int
    total_bike_slots: int
    available_car_slots: int
    available_bike_slots: int
    is_paid: bool
    price_per_hour: int
    rule_type: str
    rule_description: Optional[str] = None
    distance_km: Optional[float] = None
    earliest_free_time: Optional[str] = None

    class Config:
        from_attributes = True


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
    duration_hours: Optional[int] = None
    total_cost: Optional[int] = None

    class Config:
        from_attributes = True


class RushPredictionOut(BaseModel):
    spot_id: int
    hour: int
    day_of_week: int
    chance_of_full: str
    status: str


class SignScanOut(BaseModel):
    detected_signs: List[str]
    rule_type: str
    rule_description: str
    saved_to_db: bool
    spot_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    database: str
    total_spots: int
    active_bookings: int
    models_loaded: dict
    timestamp: datetime
