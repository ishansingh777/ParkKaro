# 🚗 ParkKaro - Smart Parking Intelligence Platform

> **"Find. Check. Park."**  
> India-focused AI parking intelligence platform with PostGIS spatial tracking, real-time availability, and live slot booking.

---

## 🏗️ Architecture

- **Database**: **Supabase (PostgreSQL 15 + PostGIS)** with spatial Point geography (`location`).
- **Backend**: **FastAPI** (`services/api`) connecting to Supabase via SQLAlchemy 2.0 & Psycopg2.
- **Frontend**: **Next.js 14 App Router** (`apps/web`) with Tailwind CSS & Leaflet (OpenStreetMap) live interactive map.

---

## 📍 5 Sample Testing Spots in Supabase

| ID | Spot Name | City | PostGIS Coordinates | Type | Pricing | Rule Description |
|:---|:---|:---|:---|:---|:---|:---|
| **1** | Rajwada Main Parking | Indore | `22.7185, 75.8553` | 🔵 PAID | ₹20/hr | Paid municipal parking: ₹20/hr cars, ₹10/hr bikes |
| **2** | Vijay Nagar Square Lot | Indore | `22.7533, 75.8937` | 🟢 ALLOWED | Free | Free public parking allowed till 10 PM |
| **3** | Sector 17 Plaza Parking | Chandigarh | `30.7415, 76.7821` | 🔵 PAID | ₹30/hr | Smart parking zone: ₹30/hr |
| **4** | Elante Side Road | Chandigarh | `30.7055, 76.8013` | 🔴 NO_PARKING | - | Strict No Parking / Tow-Away Zone 9 AM - 9 PM |
| **5** | Panaji Municipal Market | Goa | `15.4989, 73.8278` | 🔵 PAID | ₹20/hr | Pay & Park zone: ₹20/hr |

---

## 🚀 Quick Start (Running Locally)

### 1. Start the FastAPI Backend (Port 8000)

Double click `run_backend.bat` or run:
```powershell
.\run_backend.ps1
```
* Or manually:
```powershell
cd services\api
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```
API Health Check & Docs:
* Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
* Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2. Start the Next.js Frontend (Port 3000)

Double click `run_frontend.bat` or run:
```powershell
.\run_frontend.ps1
```
* Or manually:
```powershell
cd apps\web
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser!

---

## 🧪 Testing Live Booking Flow

1. Open `http://localhost:3000`.
2. Notice the **Live PostGIS Map** showing the 5 spots with color-coded pins:
   - 🟢 **Green** = Free Parking
   - 🔵 **Blue** = Paid Municipal Lot
   - 🔴 **Red** = Tow-Away / No Parking
3. Click on **"Book Slot"** on any available spot (e.g. *Rajwada Main Parking* or *Vijay Nagar*).
4. Enter your name/plate, choose vehicle (Car / Bike), choose hours, and click **Confirm & Park Now**.
5. You will see:
   - The slot count dynamically decrease in real-time in Supabase.
   - An active parking session banner appear with a countdown timer.
6. Click **"End Park"** on the session banner — the slot is immediately released and available again in Supabase!
