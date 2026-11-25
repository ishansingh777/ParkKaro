
import json
from pathlib import Path
from collections import Counter

file_path = Path.home() / "Downloads" / "goa_parking.geojson"

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

features = data["features"]

print("========== AVAILABLE PROPERTY TAGS ==========")

tag_counts = Counter()

for feature in features:
    properties = feature.get("properties") or {}
    tag_counts.update(properties.keys())

for tag, count in tag_counts.most_common():
    print(f"{tag}: {count}")

print("\n========== LOCATION-RELATED TAGS ==========")

location_tags = [
    "addr:city",
    "addr:town",
    "addr:village",
    "addr:suburb",
    "addr:place",
    "addr:district",
    "addr:street",
    "name",
    "operator"
]

for tag in location_tags:
    values = Counter(
        str((f.get("properties") or {}).get(tag))
        for f in features
        if (f.get("properties") or {}).get(tag)
    )
    print(f"\n{tag}: {dict(values.most_common(15))}")

print("\n========== 10 UNNAMED PARKING RECORDS ==========")

count = 0

for feature in features:
    properties = feature.get("properties") or {}

    if not properties.get("name"):
        print(properties)
        count += 1

        if count == 10:
            break
