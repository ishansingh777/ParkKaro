from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta, timezone
from typing import List

from database import get_db
from db_models import ParkingSpot, ActiveBooking
from schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/api", tags=["bookings"])

@router.post("/book", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(booking_in: BookingCreate, db: Session = Depends(get_db)):
    """
    Create a live parking booking with Race-Condition Lock (SELECT ... FOR UPDATE).
    Validates capacity, rule_type, and auto-calculates end_time.
    """
    # 1. Lock the spot row to prevent concurrent race condition on the last remaining slot
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == booking_in.spot_id).with_for_update().first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    if spot.rule_type == "NO_PARKING":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot book: This spot is a designated NO_PARKING / Tow-Away zone! ({spot.rule_description})"
        )

    # 2. Check active bookings capacity with row locks
    now_utc = datetime.now(timezone.utc)
    active_count = db.query(ActiveBooking).filter(
        ActiveBooking.spot_id == spot.id,
        ActiveBooking.vehicle_type == booking_in.vehicle_type,
        ActiveBooking.status == "active",
        ActiveBooking.end_time > now_utc
    ).with_for_update().count()

    total_slots = spot.total_car_slots if booking_in.vehicle_type == "car" else spot.total_bike_slots
    if active_count >= total_slots:
        raise HTTPException(
            status_code=400,
            detail=f"No {booking_in.vehicle_type} slots available at this location right now."
        )

    # 3. Create active booking
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


@router.get("/bookings", response_model=List[BookingOut])
def get_active_bookings(db: Session = Depends(get_db)):
    """Fetch all active bookings with location names and duration."""
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


@router.post("/bookings/{booking_id}/end", response_model=dict)
def end_booking(booking_id: int, db: Session = Depends(get_db)):
    """End an active parking session (frees up slot immediately)."""
    booking = db.query(ActiveBooking).filter(ActiveBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "completed"
    booking.end_time = datetime.now(timezone.utc)
    db.commit()

    return {"message": f"Parking session {booking_id} completed successfully.", "status": "completed"}
