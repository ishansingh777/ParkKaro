import csv
import json
import re
from pathlib import Path

# Input GeoJSON paths in Downloads
DOWNLOADS_DIR = Path(r"C:\Users\HP\Downloads")
OUTPUT_DIR = Path(r"C:\Users\HP\Documents\GitHub\ParkKaro\data\processed")

CITY_SOURCES = [
   {
        "city": "Indore",
        "file": DOWNLOADS_DIR / "indore_parking.geojson",
        # Bounding box covering Greater Indore including Mhow & Simrol
        "bounds": (75.65, 76.05, 22.48, 22.90),
    },
    {
        "city": "Panaji",
        "file": DOWNLOADS_DIR / "panaji_parking.geojson",
        # Bounding box covering Panaji & Tiswadi outskirts (lon_min, lon_max, lat_min, lat_max)
        "bounds": (73.75, 73.95, 15.40, 15.55),
    },
]

CLEANED_CSV_PATH = OUTPUT_DIR / "indore_panaji_cleaned.csv"
CLEANED_GEOJSON_PATH = OUTPUT_DIR / "indore_panaji_cleaned.geojson"

CSV_COLUMNS = [
    "external_spot_id",
    "name",
    "city",
    "address",
    "longitude",
    "latitude",
    "total_car_slots",
    "total_bike_slots",
    "is_paid",
    "price_per_hour",
    "rule_type",
    "rule_description",
]


def format_external_spot_id(raw_osm_id: str) -> str:
    """Convert OSM '@id' like 'way/44280183' into 'osm_way_44280183'."""
    cleaned = raw_osm_id.strip().replace("/", "_")
    if not cleaned.startswith("osm_"):
        cleaned = f"osm_{cleaned}"
    return cleaned


def parse_capacity(raw_capacity) -> str:
    """Extract positive integer capacity if available; return '' for SQL NULL."""
    if raw_capacity is None:
        return ""
    match = re.search(r"\d+", str(raw_capacity))
    if not match:
        return ""
    value = int(match.group(0))
    return str(value) if value > 0 else ""


def parse_is_paid(raw_fee) -> str:
    """Map OSM 'fee' tag to 'true', 'false', or '' (SQL NULL)."""
    if raw_fee is None:
        return ""
    fee_norm = str(raw_fee).strip().lower()
    if fee_norm == "yes":
        return "true"
    if fee_norm == "no":
        return "false"
    return ""


def build_address(props: dict, city: str) -> str:
    """Build address from OSM addr:* tags if present, else '<City>, India'."""
    parts = []
    for key in ("addr:street", "addr:suburb", "addr:district", "addr:city"):
        val = props.get(key)
        if val and str(val).strip():
            parts.append(str(val).strip())
    if parts:
        return ", ".join(parts)
    return f"{city}, India"


def build_rule_description(raw_osm_id: str, props: dict) -> str:
    """Build provenance string plus any extra descriptive OSM tags."""
    segments = [f"Imported from OpenStreetMap ({raw_osm_id})"]

    extra_fields = [
        ("operator", "Operator"),
        ("operator:type", "Operator Type"),
        ("access", "Access"),
        ("capacity", "OSM Capacity"),
        ("fee", "OSM Fee"),
        ("orientation", "Orientation"),
        ("building", "Building"),
        ("building:levels", "Building Levels"),
        ("level", "Level"),
    ]

    for key, label in extra_fields:
        val = props.get(key)
        if val is not None and str(val).strip():
            segments.append(f"{label}: {str(val).strip()}")

    return " | ".join(segments)


def process_datasets():
    cleaned_rows = []
    cleaned_features = []
    seen_external_ids = set()
    errors = []

    for source in CITY_SOURCES:
        city = source["city"]
        filepath = source["file"]
        lon_min, lon_max, lat_min, lat_max = source["bounds"]

        if not filepath.exists():
            raise FileNotFoundError(f"Missing input file: {filepath}")

        with filepath.open("r", encoding="utf-8") as f:
            data = json.load(f)

        features = data.get("features", [])
        city_count = 0
        named_count = 0

        for idx, feature in enumerate(features, start=1):
            props = feature.get("properties") or {}
            geom = feature.get("geometry") or {}

            # 1. Validate geometry
            if geom.get("type") != "Point":
                errors.append(f"[{city} #{idx}] Non-Point geometry: {geom.get('type')}")
                continue

            coords = geom.get("coordinates")
            if not isinstance(coords, list) or len(coords) < 2:
                errors.append(f"[{city} #{idx}] Invalid coordinates: {coords}")
                continue

            lon, lat = float(coords[0]), float(coords[1])
            if not (lon_min <= lon <= lon_max and lat_min <= lat <= lat_max):
                errors.append(
                    f"[{city} #{idx}] Coordinates ({lon}, {lat}) outside {city} bounds"
                )
                continue

            # 2. Validate OSM ID
            raw_osm_id = props.get("@id") or feature.get("id")
            if not raw_osm_id or not str(raw_osm_id).strip():
                errors.append(f"[{city} #{idx}] Missing OSM @id")
                continue

            raw_osm_id = str(raw_osm_id).strip()
            external_spot_id = format_external_spot_id(raw_osm_id)

            if external_spot_id in seen_external_ids:
                errors.append(f"[{city} #{idx}] Duplicate external_spot_id: {external_spot_id}")
                continue
            seen_external_ids.add(external_spot_id)

            # 3. Name with safe fallback
            raw_name = props.get("name")
            if raw_name and str(raw_name).strip():
                name = str(raw_name).strip()
                named_count += 1
            else:
                name = f"{city} Parking ({external_spot_id})"

            # 4. Remaining mapped fields
            address = build_address(props, city)
            total_car_slots = parse_capacity(props.get("capacity"))
            total_bike_slots = "10"
            is_paid = parse_is_paid(props.get("fee"))
            price_per_hour = ""  # SQL NULL

            raw_parking = props.get("parking")
            rule_type = (
                str(raw_parking).strip()
                if raw_parking and str(raw_parking).strip()
                else "ALLOWED"
            )
            rule_description = build_rule_description(raw_osm_id, props)

            row = {
                "external_spot_id": external_spot_id,
                "name": name,
                "city": city,
                "address": address,
                "longitude": f"{lon:.7f}",
                "latitude": f"{lat:.7f}",
                "total_car_slots": total_car_slots,
                "total_bike_slots": total_bike_slots,
                "is_paid": is_paid,
                "price_per_hour": price_per_hour,
                "rule_type": rule_type,
                "rule_description": rule_description,
            }
            cleaned_rows.append(row)

            cleaned_features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": row,
                }
            )
            city_count += 1

        print(
            f"{city}: processed {city_count}/{len(features)} features "
            f"({named_count} named, {city_count - named_count} fallback-named)"
        )

    if errors:
        print("\nVALIDATION ERRORS FOUND:")
        for err in errors:
            print(" -", err)
        raise SystemExit(1)

    # Write cleaned CSV
    with CLEANED_CSV_PATH.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    # Write cleaned GeoJSON
    cleaned_geojson = {"type": "FeatureCollection", "features": cleaned_features}
    with CLEANED_GEOJSON_PATH.open("w", encoding="utf-8") as geofile:
        json.dump(cleaned_geojson, geofile, ensure_ascii=False, indent=2)

    print(f"\nSuccess! Total valid records prepared: {len(cleaned_rows)}")
    print(f" - Saved CSV:     {CLEANED_CSV_PATH}")
    print(f" - Saved GeoJSON: {CLEANED_GEOJSON_PATH}")


if __name__ == "__main__":
    process_datasets()