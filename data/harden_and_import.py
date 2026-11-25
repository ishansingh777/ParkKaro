"""
ParkKaro Database Hardening & Spatial Data Import Script
- Applies PostGIS GIST spatial index on parking_spots(location)
- Adds external_spot_id column and UNIQUE constraint for clean deduplication
- Imports 77+ cleaned real parking spots for Indore and Panaji from import_indore_panaji.sql
- Ensures active_bookings has checkin audit columns
- Verifies spot distribution across cities
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load DATABASE_URL from backend/.env
ENV_PATH = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print(f"❌ DATABASE_URL not found in {ENV_PATH}")
    sys.exit(1)

SQL_FILE = Path(__file__).resolve().parent / "processed" / "import_indore_panaji.sql"

def run_hardening_and_import():
    print("==================================================")
    print("🚀 ParkKaro DB Hardening & Spatial Import")
    print("==================================================")
    print("🔌 Connecting to Supabase PostGIS...")
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # 1. PostGIS Extension
        print("\n1️⃣ Ensuring PostGIS extension is enabled...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        print("   ✅ PostGIS extension confirmed.")

        # 2. parking_spots table columns & deduplication constraint
        print("\n2️⃣ Hardening parking_spots schema...")
        cur.execute("""
            ALTER TABLE parking_spots 
            ADD COLUMN IF NOT EXISTS external_spot_id VARCHAR(100);
        """)
        # Ensure a unique index exists on external_spot_id (allows multiple NULLs in Postgres)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_parking_spots_external_spot_id 
            ON parking_spots (external_spot_id);
        """)
        print("   ✅ external_spot_id column and unique index verified.")

        # 3. GIST Spatial Index on location
        print("\n3️⃣ Creating/verifying GIST spatial index on parking_spots(location)...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_parking_spots_loc 
            ON parking_spots USING GIST (location);
        """)
        print("   ✅ GIST index 'idx_parking_spots_loc' is ACTIVE.")

        # 4. active_bookings checkin fields
        print("\n4️⃣ Verifying active_bookings check-in columns...")
        cur.execute("""
            ALTER TABLE active_bookings 
            ADD COLUMN IF NOT EXISTS is_checked_in BOOLEAN DEFAULT FALSE;
            ALTER TABLE active_bookings 
            ADD COLUMN IF NOT EXISTS check_in_time TIMESTAMP WITH TIME ZONE;
        """)
        print("   ✅ active_bookings check-in fields verified.")

        conn.commit()

        # 5. Read and execute import_indore_panaji.sql
        print(f"\n5️⃣ Reading import script: {SQL_FILE.name}...")
        if not SQL_FILE.exists():
            raise FileNotFoundError(f"Missing {SQL_FILE}")

        import_sql = SQL_FILE.read_text(encoding="utf-8")
        print("   Executing atomic insert with ON CONFLICT (external_spot_id) DO NOTHING...")
        cur.execute(import_sql)
        inserted_rows = cur.fetchall()
        conn.commit()
        print(f"   ✅ Successfully imported/updated! Rows affected: {len(inserted_rows)}")

        # 6. Verification Queries
        print("\n6️⃣ Database Verification:")
        cur.execute("""
            SELECT city, COUNT(*) as count 
            FROM parking_spots 
            GROUP BY city 
            ORDER BY count DESC;
        """)
        city_counts = cur.fetchall()
        print("   📍 Spot counts by city:")
        for city, count in city_counts:
            print(f"      - {city}: {count} spots")

        cur.execute("SELECT COUNT(*) FROM parking_spots;")
        total_spots = cur.fetchone()[0]
        print(f"   🎯 Total parking spots in database: {total_spots}")

        # Check indexes
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'parking_spots' 
            AND indexname IN ('idx_parking_spots_loc', 'uq_parking_spots_external_spot_id');
        """)
        indexes = cur.fetchall()
        print("\n   🔍 Verified Spatial & Integrity Indexes:")
        for idx_name, idx_def in indexes:
            print(f"      - {idx_name}: {idx_def}")

        print("\n==================================================")
        print("🎉 Database hardening & real spots import SUCCESSFUL!")
        print("==================================================")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during execution: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_hardening_and_import()
