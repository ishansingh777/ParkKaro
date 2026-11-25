
import json
from pathlib import Path
from collections import Counter

downloads = Path(r"C:\Users\HP\Downloads")

files = [
    "indore_parking.geojson",
    "panaji_parking.geojson"
]

for filename in files:
    path = downloads / filename

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])

    print("\n" + "=" * 55)
    print("CITY FILE:", filename)
    print("=" * 55)

    print("Total features:", len(features))

    geometry_types = Counter()
    all_keys = set()

    for feature in features:
        geometry = feature.get("geometry") or {}
        geometry_types[geometry.get("type", "Missing")] += 1
        all_keys.update(feature.get("properties") or {})

    print("\nGeometry types:")
    for geometry, count in geometry_types.items():
        print(f"{geometry}: {count}")

    print("\nAvailable property names:")
    print(sorted(all_keys))

    print("\nFirst 2 parking records:")

    for i, feature in enumerate(features[:2], 1):
        print(f"\nRecord {i}")
        print("Properties:")
        print(json.dumps(feature.get("properties"), indent=2))

        geometry = feature.get("geometry")
        print("Geometry type:", geometry.get("type") if geometry else None)
        print("Coordinates sample:")
        print(str(geometry.get("coordinates"))[:300] if geometry else None)
