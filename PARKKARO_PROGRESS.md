# 🚗 ParkKaro – Project Progress & Technical Audit Report

**Date**: November 24, 2026  
**Auditor**: Senior Full-Stack Developer & Technical Mentor  
**Target City**: Chandigarh, India  
**Target Infrastructure**: PostgreSQL + PostGIS (Supabase), FastAPI (Backend), Next.js 14 PWA (Frontend), ML Inference (Rush Predictor & Sign Scanner)

---

## 1. Executive Summary & Git Repository State

A comprehensive read-only audit of the **ParkKaro** project was conducted. 

### ⚠️ Critical Git Divergence (Local vs. Remote)
* **Local Branch Status**: Currently at commit `b6392ae` (*"ver 001"* by siddarth181717).
* **Remote Branch Status**: `origin/main` is **1 commit ahead** at `69d09cb` (*"feat: restructure to target architecture with PWA frontend, modular FastAPI backend, ML notebooks and PostGIS loader"* by Ishan Pratap Singh).
* **Impact**: The remote commit performed a fundamental architecture restructuring (moving `services/api` $\to$ `backend/` and `apps/web` $\to$ `frontend/`, introducing `ml/` pipelines, PWA manifests, camera scanner, and a PostGIS loader). The local workspace has **not yet fast-forwarded** this commit.
* **Audit Approach**: This audit analyzes **both** the currently checked-out local state and the incoming remote state to provide a complete and risk-free path forward.

---

## 2. Current Architecture

```
ParkKaro Architecture
├── Frontend (Next.js 14 App Router)
│   ├── Local State: apps/web (Standard Leaflet Map, 10s polling)
│   └── Remote State: frontend/ (PWA manifest, 2W/4W vehicle toggle, /scan camera route)
├── Backend (FastAPI + SQLAlchemy)
│   ├── Local State: services/api/app/main.py (Monolithic 278-line file)
│   └── Remote State: backend/ (Modular routers: spots.py, bookings.py, ai.py)
├── ML Subsystem (ml/)
│   ├── Rush Predictor: Random Forest / XGBoost (backend/models/parking_model.pkl)
│   └── Sign Scanner: YOLOv8 Indian Sign Detector (backend/models/sign_detector.pt placeholder)
├── Data Ingestion (data/)
│   ├── Loader: data/load_spots.py (Raw psycopg2 DDL & DML script)
│   └── Seed Datasets: data/raw/ and data/processed/ (Only 5 sample mock spots)
└── Cloud Infrastructure
    ├── Database: Supabase PostgreSQL 15 + PostGIS
    ├── Hosting Targets: Vercel (Frontend), Render / Hugging Face (Backend)
```

---

## 3. Existing Database Schema

The database design relies on two primary tables created in Supabase PostgreSQL:

### Table: `parking_spots`
| Column Name | SQL Data Type | Nullable | Default / Constraints | Notes |
|:---|:---|:---:|:---|:---|
| `id` | `SERIAL` | No | `PRIMARY KEY` | Auto-incrementing integer (1, 2, 3...) |
| `name` | `VARCHAR(255)` | No | - | Spot / parking lot title |
| `city` | `VARCHAR(100)` | No | - | City name (e.g. Chandigarh, Indore, Goa) |
| `address` | `TEXT` | Yes | `NULL` | Street address or locality description |
| `location` | `GEOGRAPHY(Point, 4326)` | No | - | WGS84 Spatial Geography Point |
| `total_car_slots` | `INTEGER` | Yes | `0` | Capacity for 4-wheelers |
| `total_bike_slots` | `INTEGER` | Yes | `0` | Capacity for 2-wheelers |
| `is_paid` | `BOOLEAN` | Yes | `FALSE` | Paid vs. free lot indicator |
| `price_per_hour` | `INTEGER` | Yes | `0` | Hourly rate in INR (₹) |
| `rule_type` | `VARCHAR(50)` | Yes | `'ALLOWED'` | Enum-like: `ALLOWED`, `PAID`, `NO_PARKING` |
| `rule_description`| `TEXT` | Yes | `NULL` | Sign text, hours, or tow-away warnings |
| `created_at` | `TIMESTAMPTZ` | Yes | `NOW()` | Timestamp |

### Table: `active_bookings`
| Column Name | SQL Data Type | Nullable | Default / Constraints | Notes |
|:---|:---|:---:|:---|:---|
| `id` | `SERIAL` | No | `PRIMARY KEY` | Auto-incrementing integer |
| `spot_id` | `INTEGER` | No | `REFERENCES parking_spots(id) ON DELETE CASCADE` | Foreign key to parking spot |
| `user_name` | `VARCHAR(100)` | No | - | Driver or vehicle owner identifier |
| `vehicle_type` | `VARCHAR(20)` | Yes | `'car'` | `'car'` or `'bike'` |
| `start_time` | `TIMESTAMPTZ` | Yes | `NOW()` | Booking start time |
| `end_time` | `TIMESTAMPTZ` | No | - | Auto-calculated expiration time |
| `status` | `VARCHAR(30)` | Yes | `'active'` | `'active'`, `'completed'`, `'cancelled'` |

### Schema Deficiencies & Vulnerabilities
1. **Missing Spatial Index**: There is **no GIST index** on `parking_spots(location)`. Proximity queries (`ST_DistanceSphere`) will perform full sequential table scans.
2. **Missing Deduplication & Unique Constraints**: `parking_spots` has no unique constraint on `(name, city)` or `location`. Re-running `data/load_spots.py` repeatedly inserts duplicate rows because `ON CONFLICT DO NOTHING` has no conflict target to latch onto.
3. **ORM Model Inconsistency**: The SQLAlchemy model in `services/api/app/models.py` (and `backend/db_models.py`) **omits the `location` column completely**. As a result, standard SQLAlchemy queries cannot read or write coordinates, forcing developers to resort to raw SQL queries. GeoAlchemy2 is missing from dependencies.
4. **No Schema Migration Management**: Alembic was deleted in commit `b6392ae`. Changes to schema are currently made via manual SQL strings inside Python scripts.

---

## 4. PostGIS Status (Verifiability & Technical Details)

* **Extension Activation**: `CREATE EXTENSION IF NOT EXISTS postgis;` is included in `data/load_spots.py`.
* **Database Connection Status**:
  * Connection String in `.env.example`:  
    `postgresql://postgres.isatsybreksmsliwmipj:Siddarth890@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres`
  * **Network Probe Result**: Host DNS resolves successfully (`3.1.167.181`), but socket connections to port `6543` timeout.
  * **Diagnosis**: The Supabase project `isatsybreksmsliwmipj` is either **paused** due to free-tier inactivity (standard Supabase behavior after 7 days) or port 6543 is blocked on the local network. Direct hostname `db.isatsybreksmsliwmipj.supabase.co` did not resolve.
* **Spatial SQL Operations Tested in Codebase**:
  * Point Extraction: `ST_X(p.location::geometry)`, `ST_Y(p.location::geometry)`.
  * Point Generation: `ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography`.
  * Nearest Neighbor: `ST_DistanceSphere(p.location::geometry, ST_SetSRID(ST_Point(:lng, :lat), 4326)) / 1000.0`.

---

## 5. Geospatial Implementation

### Positive Implementations
* **Accurate Coordinate Representation**: Data is correctly stored in WGS84 (`SRID 4326`) as `GEOGRAPHY(Point, 4326)`. This avoids projection distortion for distance computations across India.
* **Nearest-Neighbor Route**: `GET /api/nearest` in `backend/routers/spots.py` accurately filters by vehicle type (`car` vs. `bike`), excludes `NO_PARKING` zones, checks available capacity dynamically, and orders by spherical distance in kilometers.
* **Frontend Visualization**: Dynamic Leaflet map (`ParkingMap.tsx`) renders colored pins:
  * 🟢 Green: `ALLOWED` (Free public parking)
  * 🔵 Blue: `PAID` (Commercial/municipal lots)
  * 🔴 Red: `NO_PARKING` (Tow-away zones)

### Identified Gaps
* **Polygons / Way Features Not Supported**: OpenStreetMap Overpass queries export parking areas as both `node` (Point) and `way`/`relation` (Polygon). The current schema and ingestion pipeline **only support Points**. Centroid reduction is necessary for polygons.
* **Spatial Bounding Box / Viewport Querying Missing**: The API currently retrieves either all spots in a city or the nearest spots from a single coordinate. It lacks an `ST_MakeEnvelope` or bounding box (`min_lat`, `min_lng`, `max_lat`, `max_lng`) API for map viewport panning.

---

## 6. Data Import Status & Chandigarh Dataset State

### ⚠️ Critical Finding: Historical Datasets Missing from Git
The project instructions reference historical datasets gathered from OpenStreetMap:
- `export.geojson` (136 Chandigarh parking features from Overpass Turbo)
- `chandigarh_parking_cleaned.geojson`
- `chandigarh_parking_import.csv`

**Audit Finding**: None of these three files exist in the local workspace or in the git commit history.

### Current Dataset Contents in Repository:
1. `data/raw/sample_parking_overpass.geojson`: Contains only **2 mock features** from Indore.
2. `data/processed/city_spots_processed.json`: Contains only **5 mock spots** (2 Indore, 2 Chandigarh, 1 Goa).
   * Chandigarh Spot 1: *Sector 17 Plaza Parking* (`30.7415, 76.7821`, 80 cars, 200 bikes, ₹30/hr).
   * Chandigarh Spot 2: *Elante Side Road* (`30.7055, 76.8013`, 0 cars, 0 bikes, Tow-away zone).
3. `data/load_spots.py`: Hardcoded list of 6 Python dictionaries.

**Required Action**: The 136 Chandigarh OSM parking features must be either provided by the user or freshly re-extracted using an Overpass Turbo query for Chandigarh bounding box `[30.65, 76.68, 30.82, 76.87]` and converted to our schema.

---

## 7. spot_id Synchronization Status

### 🚨 Critical Vulnerability: Dynamic IDs vs. Model Invariance
1. **Database Identity**: `parking_spots.id` is generated sequentially by PostgreSQL `SERIAL`. If rows are cleared and re-imported, the IDs change (e.g. Spot #1 becomes Spot #137).
2. **ML Rush Predictor Coupling**: In `ml/rush_predictor/train_rush.ipynb` and `backend/routers/ai.py`, the Random Forest model takes `spot_id` as a raw numeric feature:
   ```python
   prob = float(rush_model.predict_proba([[spot_id, hour, day_of_week, is_weekend]])[0][1])
   ```
   * The training notebook hardcoded `spot_ids = np.random.choice([1, 2, 3, 4, 5], ...)`.
   * For any new spot with `spot_id > 5`, the decision trees fall back to the highest split, yielding distorted predictions.
   * If database IDs shift, the ML predictions map to the wrong physical locations.
3. **Loss of Source Identifier**: When importing OpenStreetMap data, the persistent `osm_id` (e.g., `way/12345678`) is discarded.
4. **Proposed Solution**:
   * Add a permanent `external_id` / `osm_id` string column to `parking_spots` with a unique index.
   * Standardize `spot_id` generation or decouple the ML model so it predicts rush based on location type, capacity, and city zone rather than arbitrary sequential integers.

---

## 8. API Integration Status

| Endpoint | Method | Local Main (`b6392ae`) | Remote Main (`69d09cb`) | Integration Status | Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| `/api/health` | GET | ❌ (`/api/v1/health`) | ✅ | Implemented | Verifies DB connection & loaded ML models |
| `/api/spots` | GET | ❌ (`/api/v1/spots`) | ✅ | Implemented | City filter + live capacity counts |
| `/api/spots/{id}` | GET | ❌ (`/api/v1/spots/{id}`) | ✅ | Implemented | Single spot details |
| `/api/nearest` | GET | ❌ Missing | ✅ | Implemented | PostGIS `ST_DistanceSphere` nearest search |
| `/api/book` | POST | ❌ (`/api/v1/bookings`) | ✅ | Implemented | Race-condition protection with `FOR UPDATE` |
| `/api/bookings` | GET | ❌ (`/api/v1/bookings`) | ✅ | Implemented | Active bookings with countdown |
| `/api/bookings/{id}/end` | POST | ❌ (`/api/v1/bookings/{id}/end`) | ✅ | Implemented | Ends session, releases slot immediately |
| `/api/predict-rush` | GET | ❌ Missing | ✅ | Implemented | Scikit-learn Random Forest model inference |
| `/api/scan-sign` | POST | ❌ Missing | ✅ | Implemented | YOLOv8 / OCR + PostGIS auto-save feedback |

* **Frontend Client**: Local frontend (`apps/web`) makes direct `fetch()` calls. Remote frontend (`frontend/src/lib/api.ts`) provides clean, typed asynchronous API helper functions.
* **Concurrency Locking**: Remote `bookings.py` correctly uses `with_for_update()` on both the parking spot and active booking query to eliminate double-booking race conditions on the final available slot.

---

## 9. Testing Status

* **Unit Tests**: **0%** (No tests found for FastAPI routers, database models, or geospatial queries).
* **Frontend Tests**: **0%** (No Jest, React Testing Library, or Vitest specs).
* **End-to-End Tests**: **0%** (No Playwright or Cypress workflows).
* **CI/CD Workflows**:
  * `.github/workflows/backend.yml` (0 bytes - empty)
  * `.github/workflows/frontend.yml` (0 bytes - empty)
  * `.github/workflows/tests.yml` (0 bytes - empty)
* **Status**: Automated test framework needs to be established from the ground up (`pytest` with SQLite/PostGIS mock + FastAPI `TestClient`).

---

## 10. Deployment Status

* **Database**: Hosted on Supabase (needs unpausing / verification of credentials).
* **Backend**: Intended for Render or Hugging Face Spaces.
  * No `render.yaml` or `Dockerfile` currently present in root or backend directory.
  * `backend/models/sign_detector.pt` contains a placeholder string (`YOLOV8_WEIGHTS_PLACEHOLDER`), which will fail if YOLO attempts to load real PyTorch weights on startup without fallback handling.
* **Frontend**: Configured for Next.js 14 / Vercel.
  * PWA manifest (`manifest.json`) and icons configured on remote branch.
  * Production environment variables (`NEXT_PUBLIC_API_URL`) require configuration on Vercel.

---

## 11. Prioritized Implementation Roadmap

Based on project responsibilities, the following small, non-destructive milestones are planned:

```
Milestone 1: Repository & Architecture Alignment
├── Review & fast-forward local branch to remote main (69d09cb)
└── Establish clean local Python virtual environment & install requirements

Milestone 2: Database Hardening & PostGIS Verification
├── Resume/verify Supabase connection
├── Add GIST spatial index: CREATE INDEX idx_parking_spots_loc ON parking_spots USING GIST (location)
├── Add external_id / osm_id column with UNIQUE constraint to prevent duplicate imports
└── Integrate GeoAlchemy2 into backend models

Milestone 3: Chandigarh Geospatial Data Pipeline
├── Ingest 136 Chandigarh parking features (extract via Overpass Turbo / process GeoJSON)
├── Clean and normalize attributes (car/bike capacity, paid vs free, rules)
├── Implement stable spot_id synchronization with deterministic hashing/OSM IDs
└── Run bulk insertion script into Supabase with ON CONFLICT (external_id) DO UPDATE

Milestone 4: Backend Decoupling & ML Alignment
├── Adjust Rush Predictor to use stable features (hour, day, weekend, spot_type, zone)
└── Add unit & integration tests with pytest and FastAPI TestClient

Milestone 5: Frontend-Backend Integration & PWA Verification
├── Verify live map rendering with all 136 Chandigarh spots
├── Test 2W/4W booking flow, nearest-neighbor routing, and active session countdown
└── Verify PWA offline manifest & Sign Scanner feedback loop

Milestone 6: Deployment & CI/CD Setup
├── Add Dockerfile & Render/Hugging Face deployment configurations
├── Add Vercel deployment configuration
└── Populate GitHub Actions CI/CD workflows (.github/workflows/)
```

---

*Report generated and ready for user review. No implementation changes will begin until approved.*
