from contextlib import asynccontextmanager
import os

# Set YOLO config directory before any ultralytics imports
os.environ.setdefault(
    "YOLO_CONFIG_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "sign_scanner", ".yolo_config"))
)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from config import settings
from database import get_db
from db_models import ParkingSpot, ActiveBooking
from schemas import HealthResponse

from routers.spots import router as spots_router
from routers.bookings import router as bookings_router
from routers.ai import router as ai_router

# In-memory dictionary for ML models loaded once on startup
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML models in memory
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    joblib_model_path = os.path.join(model_dir, "parking_occupancy_model.joblib")
    pkl_model_path = os.path.join(model_dir, "parking_model.pkl")
    sign_model_path = os.path.join(model_dir, "sign_detector.pt")

    # 1. Load Model 1: Rush Predictor (Pipeline or Random Forest)
    rush_loaded = False
    for path in [joblib_model_path, pkl_model_path]:
        if os.path.exists(path):
            try:
                import joblib
                models["rush"] = joblib.load(path)
                print(f" Loaded Model 1 (Rush Predictor): {os.path.basename(path)}")
                rush_loaded = True
                break
            except Exception as e:
                print(f"⚠️ Could not load {os.path.basename(path)}: {e}")

    if not rush_loaded:
        print("ℹ️ Rush model not found; using calibrated heuristic predictor.")
        models["rush"] = None

    # 2. Load Model 2: Sign Scanner (YOLOv8)
    if os.path.exists(sign_model_path):
        try:
            from ultralytics import YOLO
            models["sign"] = YOLO(sign_model_path)
            print(" Loaded Model 2 (Sign Scanner): sign_detector.pt")
        except Exception as e:
            print(f"⚠️ Could not load sign_detector.pt: {e}")
            models["sign"] = None
    else:
        print("ℹ️ sign_detector.pt not found; using visual sign parser.")
        models["sign"] = None

    app.state.models = models
    yield
    models.clear()


app = FastAPI(
    title="ParkKaro API",
    description="India-focused Smart Parking Intelligence API connecting to Supabase PostGIS & AI Models",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(spots_router)
app.include_router(bookings_router)
app.include_router(ai_router)

# Compatibility router for /api/v1 legacy paths
app.include_router(spots_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
@app.get("/api/v1/health", response_model=HealthResponse, tags=["health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies Supabase PostgreSQL connection and ML models."""
    try:
        spots_count = db.query(ParkingSpot).count()
        bookings_count = db.query(ActiveBooking).filter(ActiveBooking.status == "active").count()
        return HealthResponse(
            status="ok",
            database="connected",
            total_spots=spots_count,
            active_bookings=bookings_count,
            models_loaded={
                "rush_predictor": models.get("rush") is not None,
                "sign_scanner": models.get("sign") is not None
            },
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
