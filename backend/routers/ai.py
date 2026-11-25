from fastapi import APIRouter, Query, Request
from schemas import RushPredictionOut

router = APIRouter(prefix="/api", tags=["ai"])


@router.get("/predict-rush", response_model=RushPredictionOut)
def predict_rush(
    request: Request,
    spot_id: int = Query(..., description="Target parking spot ID"),
    hour: int = Query(..., ge=0, le=23, description="Hour of the day (0-23)"),
    day_of_week: int = Query(..., ge=0, le=6, description="Day of week (0=Sun, 6=Sat)")
):
    """
    Model 1: Rush Predictor (Random Forest / XGBoost).
    Predicts probability of spot being fully occupied based on historical rush patterns.
    """
    models = getattr(request.app.state, "models", {})
    rush_model = models.get("rush")

    is_weekend = 1 if day_of_week in (5, 6) else 0

    if rush_model is not None:
        try:
            # Model features: [spot_id, hour, day_of_week, is_weekend]
            prob = float(rush_model.predict_proba([[spot_id, hour, day_of_week, is_weekend]])[0][1])
        except Exception:
            prob = calculate_heuristic_rush(hour, is_weekend)
    else:
        prob = calculate_heuristic_rush(hour, is_weekend)

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
