"""User dashboard routes returning only data owned by the authenticated user."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from database import get_db
from db_models import ActiveBooking, ParkingSpot, User
from routers.bookings import auto_release_no_shows
from schemas import AuthUserOut, BookingOut

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/dashboard")
def user_dashboard(
    current_user: User = Depends(require_role("user", "developer")),
    db: Session = Depends(get_db),
):
    """Return dashboard data filtered strictly by current_user.id."""
    auto_release_no_shows(db)

    rows = (
        db.query(ActiveBooking, ParkingSpot)
        .join(ParkingSpot, ActiveBooking.spot_id == ParkingSpot.id)
        .filter(ActiveBooking.user_id == current_user.id)
        .order_by(ActiveBooking.start_time.desc(), ActiveBooking.id.desc())
        .all()
    )

    now_utc = datetime.now(timezone.utc)
    bookings_out = []
    active_count = 0
    total_spent = 0

    for booking, spot in rows:
        start_t = booking.start_time
        end_t = booking.end_time
        if start_t and end_t:
            duration_hours = max(1, int(round((end_t - start_t).total_seconds() / 3600.0)))
        else:
            duration_hours = 1
        cost = (spot.price_per_hour or 0) * duration_hours if spot.is_paid else 0
        total_spent += cost

        is_live = booking.status == "active" and (
            end_t.replace(tzinfo=timezone.utc) > now_utc if end_t and end_t.tzinfo is None else (end_t > now_utc if end_t else False)
        )
        if is_live:
            active_count += 1

        bookings_out.append(
            BookingOut(
                id=booking.id,
                spot_id=booking.spot_id,
                spot_name=spot.name,
                city=spot.city,
                user_name=booking.user_name,
                vehicle_type=booking.vehicle_type,
                start_time=booking.start_time,
                end_time=booking.end_time,
                status=booking.status,
                is_checked_in=bool(booking.is_checked_in),
                duration_hours=duration_hours,
                total_cost=cost,
            )
        )

    return {
        "user": AuthUserOut.model_validate(current_user),
        "summary": {
            "total_bookings": len(bookings_out),
            "active_bookings": active_count,
            "completed_or_past": len(bookings_out) - active_count,
            "total_spent": total_spent,
        },
        "bookings": bookings_out,
    }


@router.post("/bookings/{booking_id}/end")
def end_own_booking(
    booking_id: int,
    current_user: User = Depends(require_role("user", "developer")),
    db: Session = Depends(get_db),
):
    """Allow an authenticated user to end only their own booking (or developer)."""
    booking = db.query(ActiveBooking).filter(ActiveBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id and current_user.role != "developer":
        raise HTTPException(status_code=403, detail="Forbidden")

    booking.status = "completed"
    booking.end_time = datetime.now(timezone.utc)
    db.commit()
    return {"message": f"Parking session #{booking_id} ended.", "status": "completed"}
