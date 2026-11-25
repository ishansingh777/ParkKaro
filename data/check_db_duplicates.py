import csv
from pathlib import Path

PROJECT_DIR = Path(r"C:\Users\HP\Documents\GitHub\ParkKaro\data\processed")
CSV_PATH = PROJECT_DIR / "indore_panaji_cleaned.csv"
SQL_OUT_PATH = PROJECT_DIR / "check_db_duplicates.sql"


def sql_escape(value: str) -> str:
    """Escape single quotes for safe SQL string literals."""
    return value.replace("'", "''")


def generate_duplicate_check_sql():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {CSV_PATH}")

    values_lines = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ext_id = sql_escape(row["external_spot_id"])
            name = sql_escape(row["name"])
            city = sql_escape(row["city"])
            lon = float(row["longitude"])
            lat = float(row["latitude"])
            values_lines.append(
                f"        ('{ext_id}', '{name}', '{city}', {lon:.7f}, {lat:.7f})"
            )

    values_block = ",\n".join(values_lines)

    sql_query = f"""-- READ-ONLY DUPLICATE & PROXIMITY CHECK (Does NOT modify any data)
WITH incoming(external_spot_id, name, city, lon, lat) AS (
    VALUES
{values_block}
)
SELECT
    CASE
        WHEN p.external_spot_id = i.external_spot_id THEN 'EXACT_ID_MATCH'
        ELSE 'NEARBY_WITHIN_30M'
    END AS conflict_type,
    i.external_spot_id AS incoming_external_id,
    i.name AS incoming_name,
    i.city AS incoming_city,
    p.id AS existing_db_id,
    p.name AS existing_name,
    p.city AS existing_city,
    p.external_spot_id AS existing_external_id,
    ROUND(
        ST_Distance(
            p.location,
            ST_SetSRID(ST_MakePoint(i.lon, i.lat), 4326)::geography
        )::numeric,
        2
    ) AS distance_meters
FROM incoming i
JOIN public.parking_spots p
  ON p.external_spot_id = i.external_spot_id
  OR ST_DWithin(
      p.location,
      ST_SetSRID(ST_MakePoint(i.lon, i.lat), 4326)::geography,
      30
  )
ORDER BY conflict_type, distance_meters;
"""

    SQL_OUT_PATH.write_text(sql_query, encoding="utf-8")
    print(f"Generated read-only SQL check for {len(values_lines)} records:")
    print(f" -> {SQL_OUT_PATH}")


if __name__ == "__main__":
    generate_duplicate_check_sql()