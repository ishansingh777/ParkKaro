
import json
from pathlib import Path

downloads = Path(r"C:\Users\HP\Downloads")

files = [
    "indore_parking.geojson",
    "panaji_parking.geojson"
]

for filename in files:
    file_path = downloads / filename

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        features = data.get("features", [])

        print(f"\nFile: {filename}")
        print(f"Total features: {len(features)}")

    except Exception as e:
        print(f"\nError reading {filename}: {e}")
