# 🚗 ParkKaro - Smart Parking Intelligence Platform

> **"Find. Check. Park."**  
> India-focused AI parking intelligence platform with PostGIS spatial tracking, real-time availability, and live slot booking.

---

## 🏗️ Architecture

- **Database**: **Supabase (PostgreSQL 15 + PostGIS)** with spatial Point geography (`location`).
- **Backend & API**: **FastAPI** (`services/api`) connecting to Supabase via SQLAlchemy 2.0 & Psycopg2.
- **Frontend & UI**:
  - **Embedded Web UI** (`services/api/app/static/index.html`) served automatically on `http://localhost:8000/`.
  - **Next.js 14 Web App** (`apps/web`) with Tailwind CSS & Leaflet (OpenStreetMap) on `http://localhost:3000/`.

---

## 📍 5 Pre-seeded PostGIS Spots in Supabase

| ID | Spot Name | City | PostGIS Coordinates | Type | Pricing | Rule Description |
|:---|:---|:---|:---|:---|:---|:---|
| **1** | Rajwada Main Parking | Indore | `22.7185, 75.8553` | 🔵 PAID | ₹20/hr | Paid municipal parking: ₹20/hr cars, ₹10/hr bikes |
| **2** | Vijay Nagar Square Lot | Indore | `22.7533, 75.8937` | 🟢 ALLOWED | Free | Free public parking allowed till 10 PM |
| **3** | Sector 17 Plaza Parking | Chandigarh | `30.7415, 76.7821` | 🔵 PAID | ₹30/hr | Smart parking zone: ₹30/hr |
| **4** | Elante Side Road | Chandigarh | `30.7055, 76.8013` | 🔴 NO_PARKING | - | Strict No Parking / Tow-Away Zone 9 AM - 9 PM |
| **5** | Panaji Municipal Market | Goa | `15.4989, 73.8278` | 🔵 PAID | ₹20/hr | Pay & Park zone: ₹20/hr |

---

## 🚀 Quick Start (One-Click Launch)

### Instant All-in-One Launcher (Recommended)
Double click `start_parkkaro.bat` or run in PowerShell:
```powershell
.\start_parkkaro.ps1
```
This automatically:
1. Connects to the Supabase PostGIS database.
2. Starts the FastAPI server on port 8000.
3. Automatically opens the interactive UI in your default browser at **[http://localhost:8000](http://localhost:8000)**!

---

### Running Individual Services

#### 1. FastAPI Backend & Web UI (Port 8000)
```powershell
.\run_backend.ps1
```
* Interactive UI: [http://localhost:8000](http://localhost:8000)
* API Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
* Platform Statistics: [http://localhost:8000/api/v1/stats](http://localhost:8000/api/v1/stats)
* Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 2. Frontend Server (Port 3000)
```powershell
.\run_frontend.ps1
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser!

---

## 🎨 UI Features

1. **Interactive Live OpenStreetMap**:
   - Color-coded pins (🟢 Free, 🔵 Paid, 🔴 Tow-Away / No Parking with animated danger pulse).
   - Click markers to inspect live available slots, pricing, and book directly from the map.
2. **Real-Time Booking & Slot Occupancy**:
   - Live Car & Bike slot counters with animated capacity progress bars.
   - Dynamic pricing calculator (Free vs hourly rates).
   - Indian vehicle registration support (e.g. `MP-09-AB-1234`, `DL-01-AX-9999`).
3. **Live Parking Meters & Countdown Timers**:
   - Active parking session drawer with real-time countdown.
   - Digital Parking Pass modal with barcode simulation and ticket reference.
   - One-click "End Park" button that instantly frees up slots back in Supabase.
4. **Register New Parking Zones (PostGIS Integration)**:
   - "Add Spot" modal with PostGIS point coordinate generation.
   - Click anywhere on the map or input latitude & longitude to create new spots.
5. **City & Type Filters**:
   - Quick city filters (Indore, Chandigarh, Goa, All).
   - Filter by Free, Paid, or Tow-Away zones.
   - Search by spot name, address, or landmark.
