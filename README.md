# 🚗 ParkKaro - Smart Parking Intelligence Platform

> **"Find. Check. Park."**  
> India-focused AI parking intelligence platform with PostGIS spatial tracking, dual ML pipeline (Rush Predictor + Sign Scanner), and live 2-Wheeler / 4-Wheeler slot booking.

---

## 🏗️ Project Architecture & Directory Layout

- **Database**: **Supabase (PostgreSQL 15 + PostGIS)** with spatial Point geography (`location`).
- **Backend & Embedded Web UI**: **FastAPI** (`backend/`) serving `/home` ([home.html](backend/static/home.html)), `/` ([index.html](backend/static/index.html)), and REST APIs (`/api/*` & `/api/v1/*`) with `parkkaro99@gmail.com` feedback contact.

```
ParkKaro/
├── backend/                   # FastAPI Server + Embedded ParkKaro Web UI + Supabase/PostGIS
│   ├── static/                # ParkKaro light-theme UI (home.html, index.html, manifest.json, sw.js)
│   ├── models/                # Trained Rush Predictor models (parking_occupancy_model.joblib, .pkl)
│   ├── routers/
│   │   ├── spots.py           # /api/spots, /api/nearest, /api/stats (PostGIS spatial queries)
│   │   ├── bookings.py        # /api/book, /api/bookings, /checkin, /leave-early, /end
│   │   └── ai.py              # /api/predict-rush
│   ├── main.py                # FastAPI app entry point + CORS + static UI mount + /api/v1 compat
│   └── requirements.txt       # fastapi, uvicorn, psycopg2-binary, scikit-learn, etc.
│
├── frontend/                  # Next.js PWA
│   ├── public/                # PWA icons, manifest.json, home.html, index.html, sw.js
│   └── src/
│
├── ml/                        # Model Training & Notebooks
├── data/                      # Geospatial & City Parking Data
├── .gitignore
└── README.md
```

---

## 📍 Pre-seeded PostGIS Spots in Supabase

| ID | Spot Name | City | PostGIS Coordinates | Type | Pricing | Rule Description |
|:---|:---|:---|:---|:---|:---|:---|
| **1** | Rajwada Main Parking | Indore | `22.7185, 75.8553` | 🔵 PAID | ₹20/hr | Paid municipal parking: ₹20/hr cars, ₹10/hr bikes |
| **2** | Vijay Nagar Square Lot | Indore | `22.7533, 75.8937` | 🟢 ALLOWED | Free | Free public parking allowed till 10 PM |
| **3** | Sector 17 Plaza Parking | Chandigarh | `30.7415, 76.7821` | 🔵 PAID | ₹30/hr | Smart parking zone: ₹30/hr |
| **4** | Elante Side Road | Chandigarh | `30.7055, 76.8013` | 🔴 NO_PARKING | - | Strict No Parking / Tow-Away Zone 9 AM - 9 PM |
| **5** | Panaji Municipal Market | Goa | `15.4989, 73.8278` | 🔵 PAID | ₹20/hr | Pay & Park zone: ₹20/hr |

---

## 🚀 Quick Start

### Instant All-in-One Launcher
Double click `start_parkkaro.bat` or run in PowerShell:
```powershell
.\start_parkkaro.ps1
```

### 1. Backend & Embedded Web UI (Port 8000)

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Landing Page**: [http://localhost:8000/home](http://localhost:8000/home)
- **Live Map & App UI**: [http://localhost:8000/](http://localhost:8000/)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health) (and `/api/v1/health`)
- **Platform Stats**: [http://localhost:8000/api/stats](http://localhost:8000/api/stats) (and `/api/v1/stats`)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Next.js Frontend Setup (Port 3000)

```powershell
cd frontend
npm install
npm run dev
```

- Open **[https://parkkaro-api-production.up.railway.app/home]** in your browser or mobile device.

---

## 🎨 Embedded UI Highlights

1. **ParkKaro Light Theme & Branding**: Crisp white (`#FFFFFF`), Rapido yellow (`#FFCA20`), royal navy (`#1C4178`), and bird's-eye parked car logo.
2. **Hero AI Sign Scanner + Interactive Map**: Inline sign scanner on `/home`, Satellite / Street / Midnight map switcher, and live PostGIS parking spots on `/`.
3. **Real-Time Booking & Countdown Timers**: 2W/4W capacity counters, booking drawer, pass modal, and 1-click session completion.
4. **Feedback & Support**: Reach out anytime at `parkkaro99@gmail.com`.

---

## 📡 API Endpoints Reference

Both `/api/*` and `/api/v1/*` prefixes are supported:

### Spots & Spatial Routes (`routers/spots.py`)
- `GET /api/spots?city={city}`: Returns spots with real-time available car and bike slot counts.
- `POST /api/spots`: Creates a new parking spot with PostGIS Point geometry.
- `GET /api/spots/{spot_id}`: Spot details by ID.
- `GET /api/nearest?latitude={lat}&longitude={lng}&vehicle_type={car|bike}&limit=3`: PostGIS nearest-neighbor query.
- `GET /api/stats`: Platform-wide parking & booking statistics.

### Bookings Routes (`routers/bookings.py`)
- `POST /api/book` & `POST /api/bookings`: Creates a reservation with `SELECT ... FOR UPDATE` locking.
- `GET /api/bookings`: Returns active user parking sessions with remaining time.
- `POST /api/bookings/{id}/checkin`: 15-min GPS arrival confirmation.
- `POST /api/bookings/{id}/leave-early`: Early slot release.
- `POST /api/bookings/{id}/end`: Completes parking session and frees the slot in real time.

### AI Inference Routes (`routers/ai.py`)
- `GET /api/predict-rush?spot_id={id}&hour={0-23}&day_of_week={0-6}`: Returns occupancy probability.

### Feedback Routes (`routers/feedback.py`)
- `POST /api/feedback`: Saves user feedback into Supabase PostgreSQL and returns a direct Gmail compose link for `parkkaro99@gmail.com`.
- `GET /api/feedback`: Lists recent saved feedback submissions.

---

## 👥 Team Branch & Contribution Guide

1. **Main Branch Policy**:
   - `main`: Production-ready code.
2. **Branch Naming Conventions**:
   - `feat/frontend-<feature-name>`, `feat/backend-<endpoint>`, `feat/ml-<model-name>`, `data/<city-name>`.
