
import json
from pathlib import Path
from collections import Counter

downloads = Path(r"C:\Users\HP\Downloads")

datasets = {
    "Indore": "indore_parking.geojson",
    "Panaji": "panaji_parking.geojson"
}

for city, filename in datasets.items():

    path = downloads / filename

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])

    ids = []
    geometry_types = Counter()
    missing_ids = 0
    missing_names = 0
    invalid_coordinates = []
    duplicate_ids = []

    for i, feature in enumerate(features):

        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}

        osm_id = props.get("@id") or feature.get("id")

        if osm_id:
            ids.append(osm_id)
        else:
            missing_ids += 1

        if not props.get("name"):
            missing_names += 1

        geometry_types[geometry.get("type", "Missing")] += 1

        coords = geometry.get("coordinates")

        if (
            geometry.get("type") != "Point"
            or not isinstance(coords, list)
            or len(coords) < 2
            or not all(isinstance(x, (int, float)) for x in coords[:2])
            or not (-180 <= coords[0] <= 180)
            or not (-90 <= coords[1] <= 90)
        ):
            invalid_coordinates.append(i + 1)

    duplicates = [
        item for item, count in Counter(ids).items()
        if count > 1
    ]

    print("\n" + "=" * 45)
    print("CITY:", city)
    print("=" * 45)
    print("Total features:", len(features))
    print("Geometry types:", dict(geometry_types))
    print("Missing OSM IDs:", missing_ids)
    print("Missing names:", missing_names)
    print("Duplicate OSM IDs:", duplicates)
    print("Invalid coordinates:", invalid_coordinates)

    print("Property keys:", sorted({
        key
        for feature in features
        for key in (feature.get("properties") or {})
    }))
