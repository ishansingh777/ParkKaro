from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.config import settings
from app.database import get_db
from app.models import ParkingSpot, ActiveBooking
from app.schemas import ParkingSpotOut, BookingCreate, BookingOut, HealthResponse

app = FastAPI(
    title="ParkKaro API",
    description="India-focused Smart Parking Intelligence API connecting to Supabase PostGIS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies Supabase PostgreSQL connection."""
    try:
        spots_count = db.query(ParkingSpot).count()
        bookings_count = db.query(ActiveBooking).filter(ActiveBooking.status == "active").count()
        return HealthResponse(
            status="ok",
            database="connected",
            total_spots=spots_count,
            active_bookings=bookings_count,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )


@app.get("/api/v1/spots", response_model=List[ParkingSpotOut])
def get_parking_spots(
    city: Optional[str] = Query(None, description="Filter by city (e.g. Indore, Chandigarh, Goa)"),
    db: Session = Depends(get_db)
):
    """
    Fetch parking spots with real PostGIS coordinates and live available slot counts.
    """
    query_sql = """
        SELECT 
            p.id,
            p.name,
            p.city,
            p.address,
            ST_Y(p.location::geometry) AS latitude,
            ST_X(p.location::geometry) AS longitude,
            p.total_car_slots,
            p.total_bike_slots,
            p.is_paid,
            p.price_per_hour,
            p.rule_type,
            p.rule_description,
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'car' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_car_bookings,
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'bike' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_bike_bookings
        FROM parking_spots p
        LEFT JOIN active_bookings b ON p.id = b.spot_id
        WHERE (:city IS NULL OR LOWER(p.city) = LOWER(:city))
        GROUP BY p.id, p.name, p.city, p.address, p.location, p.total_car_slots, p.total_bike_slots, p.is_paid, p.price_per_hour, p.rule_type, p.rule_description
        ORDER BY p.id ASC;
    """

    results = db.execute(text(query_sql), {"city": city}).fetchall()

    spots_out = []
    for r in results:
        active_cars = int(r.active_car_bookings)
        active_bikes = int(r.active_bike_bookings)
        avail_cars = max(0, r.total_car_slots - active_cars)
        avail_bikes = max(0, r.total_bike_slots - active_bikes)

        spots_out.append(
            ParkingSpotOut(
                id=r.id,
                name=r.name,
                city=r.city,
                address=r.address,
                latitude=float(r.latitude),
                longitude=float(r.longitude),
                total_car_slots=r.total_car_slots,
                total_bike_slots=r.total_bike_slots,
                available_car_slots=avail_cars,
                available_bike_slots=avail_bikes,
                is_paid=r.is_paid,
                price_per_hour=r.price_per_hour,
                rule_type=r.rule_type,
                rule_description=r.rule_description
            )
        )
    return spots_out


@app.get("/api/v1/spots/{spot_id}", response_model=ParkingSpotOut)
def get_parking_spot(spot_id: int, db: Session = Depends(get_db)):
    """Fetch single spot details with live availability."""
    query_sql = """
        SELECT 
            p.id,
            p.name,
            p.city,
            p.address,
            ST_Y(p.location::geometry) AS latitude,
            ST_X(p.location::geometry) AS longitude,
            p.total_car_slots,
            p.total_bike_slots,
            p.is_paid,
            p.price_per_hour,
            p.rule_type,
            p.rule_description,
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'car' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_car_bookings,
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'bike' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_bike_bookings
        FROM parking_spots p
        LEFT JOIN active_bookings b ON p.id = b.spot_id
        WHERE p.id = :spot_id
        GROUP BY p.id, p.name, p.city, p.address, p.location, p.total_car_slots, p.total_bike_slots, p.is_paid, p.price_per_hour, p.rule_type, p.rule_description;
    """
    row = db.execute(text(query_sql), {"spot_id": spot_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    avail_cars = max(0, row.total_car_slots - int(row.active_car_bookings))
    avail_bikes = max(0, row.total_bike_slots - int(row.active_bike_bookings))

    return ParkingSpotOut(
        id=row.id,
        name=row.name,
        city=row.city,
        address=row.address,
        latitude=float(row.latitude),
        longitude=float(row.longitude),
        total_car_slots=row.total_car_slots,
        total_bike_slots=row.total_bike_slots,
        available_car_slots=avail_cars,
        available_bike_slots=avail_bikes,
        is_paid=row.is_paid,
        price_per_hour=row.price_per_hour,
        rule_type=row.rule_type,
        rule_description=row.rule_description
    )


@app.post("/api/v1/bookings", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(booking_in: BookingCreate, db: Session = Depends(get_db)):
    """
    Create a live parking booking in Supabase.
    Validates spot availability, vehicle type, and no-parking zones.
    """
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == booking_in.spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    if spot.rule_type == "NO_PARKING":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot book: This spot is a designated NO_PARKING / Tow-Away zone! ({spot.rule_description})"
        )

    # Check available capacity
    now_utc = datetime.now(timezone.utc)
    active_count = db.query(ActiveBooking).filter(
        ActiveBooking.spot_id == spot.id,
        ActiveBooking.vehicle_type == booking_in.vehicle_type,
        ActiveBooking.status == "active",
        ActiveBooking.end_time > now_utc
    ).count()

    total_slots = spot.total_car_slots if booking_in.vehicle_type == "car" else spot.total_bike_slots
    if active_count >= total_slots:
        raise HTTPException(
            status_code=400,
            detail=f"No {booking_in.vehicle_type} slots available at this location right now."
        )

    start_time = now_utc
    end_time = now_utc + timedelta(hours=booking_in.duration_hours)

    new_booking = ActiveBooking(
        spot_id=spot.id,
        user_name=booking_in.user_name,
        vehicle_type=booking_in.vehicle_type,
        start_time=start_time,
        end_time=end_time,
        status="active"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    total_cost = spot.price_per_hour * booking_in.duration_hours if spot.is_paid else 0

    return BookingOut(
        id=new_booking.id,
        spot_id=new_booking.spot_id,
        spot_name=spot.name,
        city=spot.city,
        user_name=new_booking.user_name,
        vehicle_type=new_booking.vehicle_type,
        start_time=new_booking.start_time,
        end_time=new_booking.end_time,
        status=new_booking.status,
        duration_hours=booking_in.duration_hours,
        total_cost=total_cost
    )


@app.get("/api/v1/bookings", response_model=List[BookingOut])
def get_active_bookings(db: Session = Depends(get_db)):
    """Fetch all active bookings with location names and remaining time."""
    query_sql = """
        SELECT 
            b.id,
            b.spot_id,
            p.name AS spot_name,
            p.city,
            p.price_per_hour,
            p.is_paid,
            b.user_name,
            b.vehicle_type,
            b.start_time,
            b.end_time,
            b.status
        FROM active_bookings b
        JOIN parking_spots p ON b.spot_id = p.id
        WHERE b.status = 'active' AND b.end_time > NOW()
        ORDER BY b.start_time DESC;
    """
    rows = db.execute(text(query_sql)).fetchall()

    results = []
    for r in rows:
        duration_hours = max(1, int((r.end_time - r.start_time).total_seconds() // 3600))
        cost = r.price_per_hour * duration_hours if r.is_paid else 0
        results.append(
            BookingOut(
                id=r.id,
                spot_id=r.spot_id,
                spot_name=r.spot_name,
                city=r.city,
                user_name=r.user_name,
                vehicle_type=r.vehicle_type,
                start_time=r.start_time,
                end_time=r.end_time,
                status=r.status,
                duration_hours=duration_hours,
                total_cost=cost
            )
        )
    return results


@app.post("/api/v1/bookings/{booking_id}/end", response_model=dict)
def end_booking(booking_id: int, db: Session = Depends(get_db)):
    """End an active parking session (frees up slot immediately)."""
    booking = db.query(ActiveBooking).filter(ActiveBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "completed"
    booking.end_time = datetime.now(timezone.utc)
    db.commit()

    return {"message": f"Parking session {booking_id} completed successfully.", "status": "completed"}
