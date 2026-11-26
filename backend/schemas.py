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
    external_spot_id: Optional[str] = None
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


class SignDetail(BaseModel):
    sign_key: str
    name: str
    category: str
    meaning: str
    wrong_meaning: Optional[str] = None
    driver_action: str
    parking_impact: str
    rule_type: str
    penalty: Optional[str] = None


class SignScanOut(BaseModel):
    detected_signs: List[str]
    rule_type: str
    rule_description: str
    sign_name: str = "Parking Sign"
    sign_category: str = "Traffic Sign"
    sign_meaning: str = "Traffic sign regulating vehicle movement and parking."
    wrong_meaning: Optional[str] = None
    driver_action: str = "Follow indicated sign."
    parking_impact: str = "Check local parking regulations."
    penalty_info: Optional[str] = None
    all_details: List[SignDetail] = []
    saved_to_db: bool = False
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


class FeedbackCreate(BaseModel):
    subject: str = Field("ParkKaro App Feedback", max_length=200)
    message: str = Field(..., min_length=1, max_length=3000)
    sender_email: Optional[str] = Field(None, max_length=120)
    source_page: str = Field("home", max_length=50)


class FeedbackOut(BaseModel):
    id: int
    subject: str
    message: str
    sender_email: Optional[str] = None
    source_page: str = "home"
    status: str = "saved"
    target_email: str = "parkkaro99@gmail.com"
    gmail_compose_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class SignupRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=120)

    class Config:
        # Ignore any client-supplied fields like `role`; server always assigns role="user".
        extra = "ignore"


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class AuthUserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    is_active: bool
