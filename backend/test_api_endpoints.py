import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

print("Initializing FastAPI TestClient with lifespan...")
with TestClient(app) as client:
    # 1. Health check
    res_health = client.get("/api/health")
    print(f"\n1. Health Check Response ({res_health.status_code}):")
    print(res_health.json())

    # 2. Spots check
    res_spots = client.get("/api/spots?limit=3")
    print(f"\n2. Spots Check Response ({res_spots.status_code}):")
    spots_data = res_spots.json()
    print(f"Retrieved {len(spots_data)} spots. Sample spot: {spots_data[0]['name'] if spots_data else 'None'}")

    # 3. Rush Prediction check
    res_rush = client.get("/api/predict-rush?spot_id=1&hour=18&day_of_week=5")
    print(f"\n3. Rush Predictor Check Response ({res_rush.status_code}):")
    print(res_rush.json())

print("\n--- All Backend API & Model Tests Complete! ---")
