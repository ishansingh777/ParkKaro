from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from typing import List, Optional
from database import get_db
from db_models import ActiveBooking
from schemas import ParkingSpotOut, ParkingSpotCreate, StatsResponse
from routers.bookings import auto_release_no_shows

router = APIRouter(tags=["spots"])

@router.get("/spots", response_model=List[ParkingSpotOut])
def get_parking_spots(
    city: Optional[str] = Query(None, description="Filter by city (e.g. Indore, Chandigarh, Goa)"),
    db: Session = Depends(get_db)
):
    """
    Fetch parking spots with real PostGIS coordinates and live available slot counts.
    """
    auto_release_no_shows(db)
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
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'bike' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_bike_bookings,
            MIN(CASE WHEN b.status = 'active' AND b.end_time > NOW() THEN b.end_time ELSE NULL END) AS earliest_end_time
        FROM parking_spots p
        LEFT JOIN active_bookings b ON p.id = b.spot_id
        WHERE (:city IS NULL OR LOWER(p.city) = LOWER(:city))
        GROUP BY p.id, p.name, p.city, p.address, p.location, p.total_car_slots, p.total_bike_slots, p.is_paid, p.price_per_hour, p.rule_type, p.rule_description
        ORDER BY p.id ASC;
    """

    results = db.execute(text(query_sql), {"city": city}).fetchall()

    spots_out = []
    for r in results:
        tot_cars = r.total_car_slots or 0
        tot_bikes = r.total_bike_slots or 0
        active_cars = int(r.active_car_bookings)
        active_bikes = int(r.active_bike_bookings)
        avail_cars = max(0, tot_cars - active_cars)
        avail_bikes = max(0, tot_bikes - active_bikes)

        free_time_str = None
        if (avail_cars == 0 or avail_bikes == 0) and r.earliest_end_time:
            free_time_str = r.earliest_end_time.strftime("%I:%M %p")

        spots_out.append(
            ParkingSpotOut(
                id=r.id,
                name=r.name,
                city=r.city,
                address=r.address,
                latitude=float(r.latitude),
                longitude=float(r.longitude),
                total_car_slots=tot_cars,
                total_bike_slots=tot_bikes,
                available_car_slots=avail_cars,
                available_bike_slots=avail_bikes,
                is_paid=r.is_paid or False,
                price_per_hour=r.price_per_hour or 0,
                rule_type=r.rule_type or "ALLOWED",
                rule_description=r.rule_description,
                earliest_free_time=free_time_str
            )
        )
    return spots_out


@router.get("/spots/{spot_id}", response_model=ParkingSpotOut)
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
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'bike' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_bike_bookings,
            MIN(CASE WHEN b.status = 'active' AND b.end_time > NOW() THEN b.end_time ELSE NULL END) AS earliest_end_time
        FROM parking_spots p
        LEFT JOIN active_bookings b ON p.id = b.spot_id
        WHERE p.id = :spot_id
        GROUP BY p.id, p.name, p.city, p.address, p.location, p.total_car_slots, p.total_bike_slots, p.is_paid, p.price_per_hour, p.rule_type, p.rule_description;
    """
    row = db.execute(text(query_sql), {"spot_id": spot_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    tot_cars = row.total_car_slots or 0
    tot_bikes = row.total_bike_slots or 0
    avail_cars = max(0, tot_cars - int(row.active_car_bookings))
    avail_bikes = max(0, tot_bikes - int(row.active_bike_bookings))

    free_time_str = None
    if (avail_cars == 0 or avail_bikes == 0) and row.earliest_end_time:
        free_time_str = row.earliest_end_time.strftime("%I:%M %p")

    return ParkingSpotOut(
        id=row.id,
        name=row.name,
        city=row.city,
        address=row.address,
        latitude=float(row.latitude),
        longitude=float(row.longitude),
        total_car_slots=tot_cars,
        total_bike_slots=tot_bikes,
        available_car_slots=avail_cars,
        available_bike_slots=avail_bikes,
        is_paid=row.is_paid or False,
        price_per_hour=row.price_per_hour or 0,
        rule_type=row.rule_type or "ALLOWED",
        rule_description=row.rule_description,
        earliest_free_time=free_time_str
    )


@router.get("/nearest", response_model=List[ParkingSpotOut])
def get_nearest_spots(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    vehicle_type: str = Query("car", pattern="^(car|bike)$"),
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    PostGIS Nearest Neighbor query: Finds nearest parking spots where available slots > 0.
    Uses ST_DistanceSphere for accurate real-world distance in meters.
    """
    auto_release_no_shows(db)
    query_sql = f"""
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
            (ST_DistanceSphere(p.location::geometry, ST_SetSRID(ST_Point(:lng, :lat), 4326)) / 1000.0) AS distance_km,
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'car' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_car_bookings,
            COALESCE(SUM(CASE WHEN b.vehicle_type = 'bike' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0) AS active_bike_bookings
        FROM parking_spots p
        LEFT JOIN active_bookings b ON p.id = b.spot_id
        WHERE p.rule_type != 'NO_PARKING'
        GROUP BY p.id, p.name, p.city, p.address, p.location, p.total_car_slots, p.total_bike_slots, p.is_paid, p.price_per_hour, p.rule_type, p.rule_description
        HAVING (
            CASE WHEN '{vehicle_type}' = 'car'
                 THEN (p.total_car_slots - COALESCE(SUM(CASE WHEN b.vehicle_type = 'car' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0))
                 ELSE (p.total_bike_slots - COALESCE(SUM(CASE WHEN b.vehicle_type = 'bike' AND b.status = 'active' AND b.end_time > NOW() THEN 1 ELSE 0 END), 0))
            END
        ) > 0
        ORDER BY distance_km ASC
        LIMIT :limit;
    """

    results = db.execute(text(query_sql), {"lat": latitude, "lng": longitude, "limit": limit}).fetchall()

    spots_out = []
    for r in results:
        tot_cars = r.total_car_slots or 0
        tot_bikes = r.total_bike_slots or 0
        avail_cars = max(0, tot_cars - int(r.active_car_bookings))
        avail_bikes = max(0, tot_bikes - int(r.active_bike_bookings))

        spots_out.append(
            ParkingSpotOut(
                id=r.id,
                name=r.name,
                city=r.city,
                address=r.address,
                latitude=float(r.latitude),
                longitude=float(r.longitude),
                total_car_slots=tot_cars,
                total_bike_slots=tot_bikes,
                available_car_slots=avail_cars,
                available_bike_slots=avail_bikes,
                is_paid=r.is_paid or False,
                price_per_hour=r.price_per_hour or 0,
                rule_type=r.rule_type or "ALLOWED",
                rule_description=r.rule_description,
                distance_km=round(float(r.distance_km), 2)
            )
        )
    return spots_out


@router.post("/spots", response_model=ParkingSpotOut, status_code=status.HTTP_201_CREATED)
def create_parking_spot(spot_in: ParkingSpotCreate, db: Session = Depends(get_db)):
    """Create a new parking spot with PostGIS Point geometry."""
    query_sql = """
        INSERT INTO parking_spots (
            name, city, address, location, total_car_slots, total_bike_slots,
            is_paid, price_per_hour, rule_type, rule_description
        )
        VALUES (
            :name, :city, :address, ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326),
            :total_car_slots, :total_bike_slots, :is_paid, :price_per_hour, :rule_type, :rule_description
        )
        RETURNING id;
    """
    try:
        result = db.execute(text(query_sql), {
            "name": spot_in.name,
            "city": spot_in.city,
            "address": spot_in.address,
            "longitude": spot_in.longitude,
            "latitude": spot_in.latitude,
            "total_car_slots": spot_in.total_car_slots,
            "total_bike_slots": spot_in.total_bike_slots,
            "is_paid": spot_in.is_paid,
            "price_per_hour": spot_in.price_per_hour,
            "rule_type": spot_in.rule_type,
            "rule_description": spot_in.rule_description
        })
        db.commit()
        new_id = result.fetchone()[0]
        return get_parking_spot(new_id, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create parking spot: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse)
def get_parking_stats(db: Session = Depends(get_db)):
    """Summary metrics of all spots, capacities, and active bookings."""
    spots = get_parking_spots(city=None, db=db)
    total_car = sum(s.total_car_slots for s in spots)
    total_bike = sum(s.total_bike_slots for s in spots)
    avail_car = sum(s.available_car_slots for s in spots)
    avail_bike = sum(s.available_bike_slots for s in spots)
    cities = set(s.city for s in spots)
    active_count = db.query(ActiveBooking).filter(
        ActiveBooking.status == "active",
        ActiveBooking.end_time > datetime.now(timezone.utc)
    ).count()

    return StatsResponse(
        total_spots=len(spots),
        available_car_slots=avail_car,
        available_bike_slots=avail_bike,
        total_car_slots=total_car,
        total_bike_slots=total_bike,
        active_bookings=active_count,
        cities_count=len(cities)
    )
