from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
import math

from database import get_db
from db_models import ParkingSpot
from schemas import RushPredictionOut

router = APIRouter(tags=["ai"])


@router.get("/predict-rush", response_model=RushPredictionOut)
def predict_rush(
    request: Request,
    spot_id: int = Query(..., description="Target parking spot ID"),
    hour: int = Query(..., ge=0, le=23, description="Hour of the day (0-23)"),
    day_of_week: int = Query(..., ge=0, le=6, description="Day of week (0=Sun, 6=Sat)"),
    vehicle_type: str = Query("car", pattern="^(car|bike)$"),
    db: Session = Depends(get_db)
):
    """
    Model 1: Rush Predictor (HistGradientBoosting / Random Forest).
    Predicts occupancy percentage and rush level based on spot attributes, time, and day.
    Includes feature adapter bridging live API queries to the trained ML Pipeline.
    """
    models = getattr(request.app.state, "models", {})
    rush_model = models.get("rush")

    is_weekend = 1 if day_of_week in (5, 6) else 0

    # Retrieve spot context from database (safe non-blocking lookup)
    city_zone = "Indore"
    total_slots = 50
    price = 20
    try:
        spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
        if spot:
            city_zone = spot.city
            total_slots = spot.total_car_slots + spot.total_bike_slots
            price = spot.price_per_hour
    except Exception:
        pass

    prob = None

    if rush_model is not None:
        # Approach 1: Try DataFrame input for scikit-learn Pipeline (ColumnTransformer + HistGradientBoosting)
        try:
            import pandas as pd

            entry_est = 14 if (17 <= hour <= 21) else (8 if 12 <= hour <= 14 else 3)
            exit_est = 11 if (17 <= hour <= 21) else (7 if 12 <= hour <= 14 else 3)

            input_df = pd.DataFrame([{
                "zone": city_zone,
                "vehicle_type": vehicle_type,
                "total_slots": total_slots,
                "avg_parking_duration_minutes": 60.0,
                "entry_count": entry_est,
                "exit_count": exit_est,
                "net_flow": entry_est - exit_est,
                "parking_fee_collected": price * entry_est,
                "fee_per_entry": float(price),
                "violation_flag": 0,
                "hour": hour,
                "dayofweek": day_of_week,
                "day": datetime.now().day,
                "month": datetime.now().month,
                "is_weekend": is_weekend
            }])

            if hasattr(rush_model, "predict"):
                raw_pred = float(rush_model.predict(input_df)[0])
                # If prediction is 0-100 percentage
                prob = (raw_pred / 100.0) if raw_pred > 1.0 else raw_pred
        except Exception:
            # Approach 2: Try basic array input for simpler classifiers
            try:
                if hasattr(rush_model, "predict_proba"):
                    prob = float(rush_model.predict_proba([[spot_id, hour, day_of_week, is_weekend]])[0][1])
            except Exception:
                pass

    # Approach 3: Fallback heuristic calibrated for Indian urban traffic rush
    if prob is None or math.isnan(prob):
        prob = calculate_heuristic_rush(hour, is_weekend)

    # Bound probability between 5% and 95%
    prob = min(0.95, max(0.05, prob))
    percentage = int(round(prob * 100))

    if prob >= 0.70:
        status_label = "Hard to find parking"
    elif prob >= 0.40:
        status_label = "Moderate rush"
    else:
        status_label = "Likely available"

    return RushPredictionOut(
        spot_id=spot_id,
        hour=hour,
        day_of_week=day_of_week,
        chance_of_full=f"{percentage}%",
        status=status_label
    )


def calculate_heuristic_rush(hour: int, is_weekend: int) -> float:
    """Heuristic Indian urban parking traffic baseline when ML model weights are training."""
    # Peak lunch rush (12-14) and evening market rush (17-21)
    if 17 <= hour <= 21:
        base = 0.82 if is_weekend else 0.75
    elif 12 <= hour <= 14:
        base = 0.65
    elif 9 <= hour <= 11:
        base = 0.55
    elif 22 <= hour or hour <= 6:
        base = 0.15
    else:
        base = 0.35
    return min(0.95, max(0.05, base))
