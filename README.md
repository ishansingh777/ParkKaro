# 🚗 ParkKaro - Smart Parking Intelligence Platform

> **"Find. Check. Park."**  
> India-focused AI parking intelligence platform with PostGIS spatial tracking, dual ML pipeline (Rush Predictor + Sign Scanner), and live 2-Wheeler / 4-Wheeler slot booking.

---

## 🏗️ Project Architecture & Directory Layout

```
ParkKaro/
├── frontend/                  # Next.js PWA (Map UI, Bottom Sheet, Sign Scanner)
│   ├── public/
│   │   ├── manifest.json      # PWA app name, icons, "Add to Home Screen" config
│   │   └── icons/             # PWA icons (192x192, 512x512)
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx     # Global styles, fonts, PWA metadata
│   │   │   ├── page.tsx       # Main Map screen + 2W/4W toggle + floating controls
│   │   │   └── scan/
│   │   │       └── page.tsx   # Camera Sign Scanner screen (YOLOv8 + OCR)
│   │   ├── components/
│   │   │   ├── ParkingMap.tsx # Leaflet map with Green/Blue/Red pins
│   │   │   ├── SpotCard.tsx   # Bottom sheet (slots, timer, Book Now, nearest spots)
│   │   │   └── RushBadge.tsx  # AI rush prediction indicator (e.g., "7 PM: 82% full")
│   │   └── lib/
│   │       └── api.ts         # Functions calling FastAPI (/spots, /book, /nearest, etc.)
│   ├── .env.local             # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
│   └── package.json
│
├── backend/                   # FastAPI Server + Supabase/PostGIS + ML Inference
│   ├── models/
│   │   ├── parking_model.pkl  # Trained Rush Predictor model (Random Forest)
│   │   └── sign_detector.pt   # Trained YOLOv8 sign model
│   ├── routers/
│   │   ├── spots.py           # /api/spots, /api/nearest (PostGIS spatial query)
│   │   ├── bookings.py        # /api/book (FOR UPDATE lock), release/timer logic
│   │   └── ai.py              # /api/predict-rush, /api/scan-sign (+ Smart Feedback)
│   ├── main.py                # FastAPI app entry point + CORS + startup model load
│   ├── .env                   # DATABASE_URL=postgresql://...
│   └── requirements.txt       # fastapi, uvicorn, psycopg2-binary, scikit-learn, etc.
│
├── ml/                        # Model Training & Notebooks (Colab sync / experiments)
│   ├── rush_predictor/
│   │   ├── train_rush.ipynb   # Random Forest / XGBoost training & evaluation
│   │   └── data/              # Raw/processed Kaggle CSVs (git-ignored)
│   └── sign_scanner/
│       ├── train_yolo.ipynb   # YOLOv8 fine-tuning notebook
│       └── data.yaml          # Dataset class mapping for Indian signs
│
├── data/                      # Geospatial & City Parking Data
│   ├── raw/                   # Overpass Turbo GeoJSON, Google Earth KML exports
│   ├── processed/             # Cleaned GeoJSON / CSV mapped with spot_id
│   └── load_spots.py          # Script to push city parking spots into Supabase PostGIS
│
├── .gitignore                 # Ignore node_modules, __pycache__, .env, large datasets
└── README.md                  # Setup steps, API endpoints, and team branch guide
```

---

## ⚡ Quick Start (Running Locally)

### 1. Backend Setup (FastAPI & PostGIS)

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup (Next.js PWA)

```powershell
cd frontend
npm install
npm run dev
```

- Open **[http://localhost:3000](http://localhost:3000)** in your browser or mobile device.
- For Camera Sign Scanner: Open **[http://localhost:3000/scan](http://localhost:3000/scan)**.

---

## 📡 API Endpoints Reference

### Spots & Spatial Routes (`routers/spots.py`)
- `GET /api/spots?city={city}`: Returns spots with real-time available car and bike slot counts.
- `GET /api/spots/{spot_id}`: Spot details by ID.
- `GET /api/nearest?latitude={lat}&longitude={lng}&vehicle_type={car|bike}&limit=3`: PostGIS nearest-neighbor query for available spots.

### Bookings Routes (`routers/bookings.py`)
- `POST /api/book`: Creates a reservation with `SELECT ... FOR UPDATE` race-condition locking.
- `GET /api/bookings`: Returns active user parking sessions with remaining time.
- `POST /api/bookings/{id}/end`: Completes parking session and frees the slot in real time.

### AI Inference Routes (`routers/ai.py`)
- `GET /api/predict-rush?spot_id={id}&hour={0-23}&day_of_week={0-6}`: Returns occupancy probability from Model 1 (e.g. `82% full`, `Hard to find parking`).
- `POST /api/scan-sign`: Uploads a parking sign photo, classifies rule via YOLOv8 / OCR, and automatically saves new unmapped spots to PostGIS (Smart Feedback Loop).

---

## 👥 Team Branch & Contribution Guide

1. **Main Branch Policy**:
   - `main`: Production-ready code. Do not push directly to `main`.
2. **Branch Naming Conventions**:
   - `feat/frontend-<feature-name>`: Frontend UI, PWA, or client features (e.g., `feat/frontend-sign-camera`).
   - `feat/backend-<endpoint>`: FastAPI backend endpoints, database, or PostGIS logic (e.g., `feat/backend-race-condition`).
   - `feat/ml-<model-name>`: Model training, dataset cleaning, or Colab sync (e.g., `feat/ml-yolo-signs`).
   - `data/<city-name>`: Geospatial KML/GeoJSON ingestion for target cities.
3. **Pull Request Workflow**:
   - Create branch from `main`: `git checkout -b feat/ml-rush-predictor`
   - Test locally using `.\run_backend.bat` and `.\run_frontend.bat`.
   - Submit PR with clear description of tested features.
