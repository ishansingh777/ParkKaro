"""
ParkKaro - City Parking Spot Loader (Supabase PostGIS)
Pushes cleaned city parking spots (Indore, Chandigarh, Goa) into Supabase PostgreSQL + PostGIS.
"""

import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

DATABASE_URL = os.getenv("DATABASE_URL")

SAMPLE_SPOTS = [
    {
        "name": "Rajwada Main Parking",
        "city": "Indore",
        "address": "MG Road, Rajwada, Indore",
        "lat": 22.7185,
        "lng": 75.8553,
        "cars": 45,
        "bikes": 120,
        "is_paid": True,
        "price": 20,
        "rule_type": "PAID",
        "rule_desc": "Municipal paid multi-level parking: ₹20/hr cars, ₹10/hr bikes"
    },
    {
        "name": "Vijay Nagar Square Public Lot",
        "city": "Indore",
        "address": "AB Road, Vijay Nagar, Indore",
        "lat": 22.7533,
        "lng": 75.8937,
        "cars": 30,
        "bikes": 60,
        "is_paid": False,
        "price": 0,
        "rule_type": "ALLOWED",
        "rule_desc": "Free public roadside parking allowed till 10 PM"
    },
    {
        "name": "Sector 17 Plaza Parking",
        "city": "Chandigarh",
        "address": "Sector 17 Commercial Complex, Chandigarh",
        "lat": 30.7415,
        "lng": 76.7821,
        "cars": 80,
        "bikes": 200,
        "is_paid": True,
        "price": 30,
        "rule_type": "PAID",
        "rule_desc": "Smart municipal paid zone: ₹30/hr"
    },
    {
        "name": "Elante Road Tow-Away Zone",
        "city": "Chandigarh",
        "address": "Purv Marg, Industrial Area Phase 1, Chandigarh",
        "lat": 30.7055,
        "lng": 76.8013,
        "cars": 0,
        "bikes": 0,
        "is_paid": False,
        "price": 0,
        "rule_type": "NO_PARKING",
        "rule_desc": "Strict No Parking / Tow-Away Zone 9 AM - 9 PM"
    },
    {
        "name": "Panaji Municipal Market Pay & Park",
        "city": "Goa",
        "address": "Near Inox, Panaji, Goa",
        "lat": 15.4989,
        "lng": 73.8278,
        "cars": 50,
        "bikes": 100,
        "is_paid": True,
        "price": 20,
        "rule_type": "PAID",
        "rule_desc": "Designated Pay & Park zone: ₹20/hr"
    },
    {
        "name": "Calangute Beach Road Free Bay",
        "city": "Goa",
        "address": "Calangute Beach Road, North Goa",
        "lat": 15.5442,
        "lng": 73.7553,
        "cars": 25,
        "bikes": 80,
        "is_paid": False,
        "price": 0,
        "rule_type": "ALLOWED",
        "rule_desc": "Free tourist parking bay"
    }
]

def load_spots():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set. Check backend/.env")
        return

    print("🔌 Connecting to Supabase PostGIS...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Ensure PostGIS extension & table exist
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parking_spots (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            city VARCHAR(100) NOT NULL,
            address TEXT,
            location GEOGRAPHY(Point, 4326) NOT NULL,
            total_car_slots INTEGER DEFAULT 0,
            total_bike_slots INTEGER DEFAULT 0,
            is_paid BOOLEAN DEFAULT FALSE,
            price_per_hour INTEGER DEFAULT 0,
            rule_type VARCHAR(50) DEFAULT 'ALLOWED',
            rule_description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_bookings (
            id SERIAL PRIMARY KEY,
            spot_id INTEGER REFERENCES parking_spots(id) ON DELETE CASCADE,
            user_name VARCHAR(100) NOT NULL,
            vehicle_type VARCHAR(20) DEFAULT 'car',
            start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            end_time TIMESTAMP WITH TIME ZONE NOT NULL,
            status VARCHAR(30) DEFAULT 'active'
        );
    """)

    insert_sql = """
        INSERT INTO parking_spots (
            name, city, address, location, total_car_slots, total_bike_slots,
            is_paid, price_per_hour, rule_type, rule_description
        ) VALUES (
            %(name)s, %(city)s, %(address)s,
            ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326)::geography,
            %(cars)s, %(bikes)s, %(is_paid)s, %(price)s, %(rule_type)s, %(rule_desc)s
        )
        ON CONFLICT DO NOTHING;
    """

    print(f"📥 Loading {len(SAMPLE_SPOTS)} city spots into PostGIS...")
    for spot in SAMPLE_SPOTS:
        cur.execute(insert_sql, spot)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ City parking spots loaded successfully into Supabase PostGIS!")

if __name__ == "__main__":
    load_spots()
