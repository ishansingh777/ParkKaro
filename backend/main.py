from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from config import settings
from database import get_db, engine
from db_models import ParkingSpot, ActiveBooking, FeedbackSubmission
from schemas import HealthResponse

from routers.spots import router as spots_router
from routers.bookings import router as bookings_router
from routers.ai import router as ai_router
from routers.feedback import router as feedback_router

# In-memory dictionary for ML models loaded once on startup
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure check-in columns & feedback table exist in Supabase
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE active_bookings "
                "ADD COLUMN IF NOT EXISTS is_checked_in BOOLEAN DEFAULT FALSE, "
                "ADD COLUMN IF NOT EXISTS check_in_time TIMESTAMPTZ;"
            ))
        FeedbackSubmission.__table__.create(bind=engine, checkfirst=True)
    except Exception as e:
        print(f"Schema check warning: {e}")

    # Load ML models in memory
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    joblib_model_path = os.path.join(model_dir, "parking_occupancy_model.joblib")
    pkl_model_path = os.path.join(model_dir, "parking_model.pkl")

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

# Include Routers under /api, /api/v1, and direct root compatibility prefix
app.include_router(spots_router, prefix="/api")
app.include_router(bookings_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")

app.include_router(spots_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")

app.include_router(spots_router)
app.include_router(bookings_router)
app.include_router(ai_router)
app.include_router(feedback_router)


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
                "rush_predictor": models.get("rush") is not None
            },
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )


# --- Static UI Mount & PWA Routing ---
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/home", include_in_schema=False)
def serve_home():
    """Serves the ParkKaro marketing landing page."""
    home_file = STATIC_DIR / "home.html"
    if home_file.exists():
        return FileResponse(str(home_file))
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/", include_in_schema=False)
@app.get("/app", include_in_schema=False)
def serve_ui():
    """Serves the main ParkKaro interactive web UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "ParkKaro API is running. UI file not found in static folder."}


@app.get("/manifest.json", include_in_schema=False)
def serve_manifest():
    manifest_file = STATIC_DIR / "manifest.json"
    if manifest_file.exists():
        return FileResponse(str(manifest_file), media_type="application/manifest+json")
    raise HTTPException(status_code=404, detail="manifest.json not found")


@app.get("/sw.js", include_in_schema=False)
def serve_sw():
    sw_file = STATIC_DIR / "sw.js"
    if sw_file.exists():
        return FileResponse(str(sw_file), media_type="application/javascript")
    raise HTTPException(status_code=404, detail="sw.js not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
