
import json
from collections import Counter
from pathlib import Path

file_path = Path.home() / "Downloads" / "goa_parking.geojson"

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

features = data.get("features", [])

geometry_counts = Counter()
osm_ids = []
missing_names = 0
missing_ids = 0
missing_geometry = 0
invalid_coordinates = 0

def check_coordinates(coords):
    global invalid_coordinates

    if isinstance(coords, list) and len(coords) >= 2:
        if all(isinstance(x, (int, float)) for x in coords[:2]):
            lon, lat = coords[0], coords[1]

            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                invalid_coordinates += 1
        else:
            for item in coords:
                check_coordinates(item)

for feature in features:
    properties = feature.get("properties") or {}
    geometry = feature.get("geometry")

    if not properties.get("name"):
        missing_names += 1

    osm_id = properties.get("@id") or feature.get("id")

    if osm_id is None:
        missing_ids += 1
    else:
        osm_ids.append(str(osm_id))

    if not geometry:
        missing_geometry += 1
    else:
        geometry_counts[geometry.get("type", "Unknown")] += 1
        check_coordinates(geometry.get("coordinates", []))

duplicate_ids = [
    osm_id for osm_id, count in Counter(osm_ids).items()
    if count > 1
]

print("\n========== GOA PARKING VALIDATION ==========")
print("Total records:", len(features))
print("Geometry types:", dict(geometry_counts))
print("Missing names:", missing_names)
print("Missing OSM IDs:", missing_ids)
print("Missing geometry:", missing_geometry)
print("Invalid coordinates:", invalid_coordinates)
print("Duplicate OSM IDs:", duplicate_ids)

print("\n========== FIRST 5 RECORDS ==========")

for feature in features[:5]:
    print({
        "id": feature.get("properties", {}).get("@id"),
        "name": feature.get("properties", {}).get("name"),
        "amenity": feature.get("properties", {}).get("amenity"),
        "geometry": feature.get("geometry", {}).get("type")
        if feature.get("geometry") else None
    })

print("\n========== VALIDATION COMPLETE ==========")
