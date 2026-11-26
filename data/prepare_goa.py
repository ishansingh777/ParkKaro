
import json
import csv
from pathlib import Path

source = Path.home() / "Downloads" / "goa_parking.geojson"
output = Path.home() / "Downloads" / "goa_parking_import.csv"

with open(source, "r", encoding="utf-8") as file:
    data = json.load(file)

rows = []
seen_ids = set()

for feature in data["features"]:
    properties = feature.get("properties") or {}
    geometry = feature.get("geometry")

    if not geometry or geometry.get("type") != "Point":
        continue


    osm_id = properties.get("@id") or feature.get("id")
    coordinates = geometry.get("coordinates", [])

    if not osm_id or len(coordinates) < 2:
        continue

    osm_id = str(osm_id)

    if osm_id in seen_ids:
        continue

    seen_ids.add(osm_id)

    longitude = float(coordinates[0])
    latitude = float(coordinates[1])

    # Keep coordinates within the broad Goa-area bounds.
    if not (73 <= longitude <= 75 and 14 <= latitude <= 16):
        continue

    name = properties.get("name") or f"Unnamed Parking ({osm_id})"

    rows.append({
        "osm_id": osm_id,
        "name": name,
        "longitude": longitude,
        "latitude": latitude,
        "properties_json": json.dumps(
            properties, ensure_ascii=False
        )
    })

with open(output, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "osm_id",
            "name",
            "longitude",
            "latitude",
            "properties_json"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print("========== GOA CSV PREPARATION ==========")
print("Records prepared:", len(rows))
print("Unique OSM IDs:", len(seen_ids))
print("Output file:", output)
print("File size:", output.stat().st_size, "bytes")
print("=========================================")
