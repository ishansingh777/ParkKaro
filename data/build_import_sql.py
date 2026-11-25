import csv
from pathlib import Path

PROJECT_DIR = Path(r"C:\Users\HP\Documents\GitHub\ParkKaro\data\processed")
CSV_PATH = PROJECT_DIR / "indore_panaji_cleaned.csv"
SQL_PATH = PROJECT_DIR / "import_indore_panaji.sql"


def sql_text(value: str) -> str:
    """Format a string as a typed SQL literal, or NULL::text if blank."""
    if value is None or value.strip() == "":
        return "NULL::text"
    escaped = value.strip().replace("'", "''")
    return f"'{escaped}'::text"


def sql_int(value: str) -> str:
    """Format an integer as a typed SQL literal, or NULL::integer if blank."""
    if value is None or value.strip() == "":
        return "NULL::integer"
    return f"{int(value.strip())}::integer"


def sql_bool(value: str) -> str:
    """Format a boolean as a typed SQL literal, or NULL::boolean if blank."""
    if value is None or value.strip() == "":
        return "NULL::boolean"
    norm = value.strip().lower()
    if norm in ("true", "false"):
        return f"{norm}::boolean"
    raise ValueError(f"Invalid boolean value: {value}")


def generate_import_sql():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {CSV_PATH}")

    values_rows = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lon = float(row["longitude"])
            lat = float(row["latitude"])

            values_rows.append(
                "    ("
                f"{sql_text(row['external_spot_id'])}, "
                f"{sql_text(row['name'])}, "
                f"{sql_text(row['city'])}, "
                f"{sql_text(row['address'])}, "
                f"{lon:.7f}::double precision, "
                f"{lat:.7f}::double precision, "
                f"{sql_int(row['total_car_slots'])}, "
                f"{sql_int(row['total_bike_slots'])}, "
                f"{sql_bool(row['is_paid'])}, "
                f"{sql_int(row['price_per_hour'])}, "
                f"{sql_text(row['rule_type'])}, "
                f"{sql_text(row['rule_description'])}"
                ")"
            )

    if not values_rows:
        raise RuntimeError("No rows found in indore_panaji_cleaned.csv")

    values_block = ",\n".join(values_rows)

    sql_script = f"""-- ParkKaro Single-Statement Atomic Import: Indore (28) & Panaji (49)
-- Preserves all existing Chandigarh, Crowdsourced, Goa, and manual Indore records.

WITH incoming (
    external_spot_id,
    name,
    city,
    address,
    longitude,
    latitude,
    total_car_slots,
    total_bike_slots,
    is_paid,
    price_per_hour,
    rule_type,
    rule_description
) AS (
    VALUES
{values_block}
)
INSERT INTO public.parking_spots (
    name,
    city,
    address,
    location,
    total_car_slots,
    total_bike_slots,
    is_paid,
    price_per_hour,
    rule_type,
    rule_description,
    external_spot_id
)
SELECT
    i.name,
    i.city,
    i.address,
    ST_SetSRID(ST_MakePoint(i.longitude, i.latitude), 4326)::geography,
    i.total_car_slots,
    i.total_bike_slots,
    i.is_paid,
    i.price_per_hour,
    i.rule_type,
    i.rule_description,
    i.external_spot_id
FROM incoming i
ON CONFLICT (external_spot_id) DO NOTHING
RETURNING id, city, name, external_spot_id;
"""

    SQL_PATH.write_text(sql_script, encoding="utf-8")
    print(f"Generated single-statement SQL for {len(values_rows)} records:")
    print(f" -> {SQL_PATH}")


if __name__ == "__main__":
    generate_import_sql()