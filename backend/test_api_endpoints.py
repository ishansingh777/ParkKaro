import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

print("==================================================")
print("🧪 Running Comprehensive ParkKaro API Tests")
print("==================================================")

with TestClient(app) as client:
    # 1. Health check
    res_health = client.get("/api/health")
    print(f"\n1. Health Check Response ({res_health.status_code}):")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print(f"   Status: {res_health.json()}")

    # 2. Spots check - All cities
    print("\n2. Checking Real Spots Data by City:")
    for city in ["Indore", "Panaji", "Goa", "Chandigarh"]:
        res_city = client.get(f"/api/spots?city={city}")
        assert res_city.status_code == 200, f"Spots query for {city} failed: {res_city.text}"
        data = res_city.json()
        print(f"   📍 {city}: Retrieved {len(data)} spots.")
        if data:
            print(f"      Sample: '{data[0]['name']}' at ({data[0]['latitude']:.4f}, {data[0]['longitude']:.4f})")

    # 3. PostGIS Nearest Neighbor Spatial Proximity Query
    print("\n3. Testing PostGIS GIST-indexed Nearest Neighbor Query:")
    # Indore coordinates (Rajwada: 22.7185, 75.8553)
    res_nearest_indore = client.get("/api/nearest?latitude=22.7185&longitude=75.8553&vehicle_type=car&limit=3")
    assert res_nearest_indore.status_code == 200, f"Nearest Indore failed: {res_nearest_indore.text}"
    nearest_indore = res_nearest_indore.json()
    print(f"   🚗 Nearest to Indore Rajwada (Cars): {len(nearest_indore)} spots returned")
    for spot in nearest_indore:
        print(f"      - {spot['name']} ({spot['city']}) | Dist: {spot.get('distance_km', 'N/A')} km | Avail Cars: {spot['available_car_slots']}")

    # Panaji coordinates (Panaji Church: 15.4989, 73.8278)
    res_nearest_panaji = client.get("/api/nearest?latitude=15.4989&longitude=73.8278&vehicle_type=bike&limit=3")
    assert res_nearest_panaji.status_code == 200, f"Nearest Panaji failed: {res_nearest_panaji.text}"
    nearest_panaji = res_nearest_panaji.json()
    print(f"   🏍️ Nearest to Panaji Market (Bikes): {len(nearest_panaji)} spots returned")
    for spot in nearest_panaji:
        print(f"      - {spot['name']} ({spot['city']}) | Dist: {spot.get('distance_km', 'N/A')} km | Avail Bikes: {spot['available_bike_slots']}")

    # 4. Rush Prediction check
    print("\n4. Testing ML Rush Prediction Pipeline:")
    res_rush = client.get("/api/predict-rush?spot_id=1&hour=19&day_of_week=5")
    assert res_rush.status_code == 200, f"Rush prediction failed: {res_rush.text}"
    rush_data = res_rush.json()
    print(f"   Peak Friday 7 PM: {rush_data}")

    res_rush_calm = client.get("/api/predict-rush?spot_id=1&hour=3&day_of_week=2")
    assert res_rush_calm.status_code == 200
    rush_calm = res_rush_calm.json()
    print(f"   Off-peak Tuesday 3 AM: {rush_calm}")

    # 5. Live Booking Flow Verification
    print("\n5. Testing Live Booking & GPS Check-in Lifecycle:")
    # Pick a spot with available car slots
    test_spot_id = nearest_indore[0]["id"] if nearest_indore else 1
    book_payload = {
        "spot_id": test_spot_id,
        "user_name": "Test Integration Runner",
        "vehicle_type": "car",
        "duration_hours": 2
    }
    res_book = client.post("/api/book", json=book_payload)
    assert res_book.status_code in (200, 201), f"Booking creation failed: {res_book.text}"
    booking = res_book.json()
    booking_id = booking["id"]
    print(f"   ✅ Booking created successfully! ID: {booking_id}, spot_id: {test_spot_id}")

    # Test GPS Check-in
    checkin_payload = {
        "booking_id": booking_id,
        "latitude": nearest_indore[0]["latitude"] if nearest_indore else 22.7185,
        "longitude": nearest_indore[0]["longitude"] if nearest_indore else 75.8553
    }
    res_checkin = client.post(f"/api/bookings/{booking_id}/checkin", json=checkin_payload)
    assert res_checkin.status_code == 200, f"GPS check-in failed: {res_checkin.text}"
    print(f"   ✅ GPS Check-in verified: {res_checkin.json()['message']}")

    # Test Early Release
    res_leave = client.post(f"/api/bookings/{booking_id}/leave-early")
    assert res_leave.status_code == 200, f"Early release failed: {res_leave.text}"
    print(f"   ✅ Early Slot Release verified: {res_leave.json()['message']}")

    # 6. Testing Verified Driver Authentication & Supabase Storage Lifecycle
    print("\n6. Testing Verified Driver Authentication Flow (Supabase):")
    import time
    ts = int(time.time())
    test_email = f"verified_driver_{ts}@parkkaro.in"
    test_phone = f"+9198765{str(ts)[-5:]}"
    signup_payload = {
        "full_name": "Test Verified Driver",
        "email": test_email,
        "phone_number": test_phone,
        "vehicle_number": "MP09AB9999",
        "password": "Password123!"
    }

    # Step A: Signup
    res_signup = client.post("/api/auth/signup", json=signup_payload)
    assert res_signup.status_code == 201, f"Signup failed: {res_signup.text}"
    signup_data = res_signup.json()
    print(f"   ✅ Sign Up Success: {signup_data['status']}")
    print(f"      - Registered User: {signup_data['user']['email']} (is_verified={signup_data['is_verified']})")
    otp_code = signup_data.get("verification_code_hint")
    assert otp_code, "Verification code not generated"
    print(f"      - Generated 6-Digit Verification Code: {otp_code}")

    # Step B: Login before verification (should require verification)
    res_prelogin = client.post("/api/auth/login", json={"email_or_phone": test_email, "password": "Password123!"})
    assert res_prelogin.status_code == 200
    assert res_prelogin.json()["is_verified"] is False, "Unverified user must not have is_verified=True"
    print(f"   ✅ Gatekeeper Verified: Unverified login correctly intercepted ({res_prelogin.json()['status']})")

    # Step C: Verify Account with 6-digit Code
    res_verify = client.post("/api/auth/verify", json={"email": test_email, "verification_code": otp_code})
    assert res_verify.status_code == 200, f"Verification failed: {res_verify.text}"
    verify_data = res_verify.json()
    assert verify_data["is_verified"] is True
    print(f"   ✅ Account Verified in Supabase: {verify_data['message']}")

    # Step D: Login after verification (should succeed with token)
    res_login = client.post("/api/auth/login", json={"email_or_phone": test_email, "password": "Password123!"})
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert login_data["is_verified"] is True
    token = login_data["token"]
    assert token, "Token not returned upon login"
    print(f"   ✅ Verified Login Successful! Profile: {login_data['user']['full_name']} | Vehicle: {login_data['user']['vehicle_number']}")

    # Step E: Authenticated /auth/me call with Bearer Token
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["email"] == test_email
    print(f"   ✅ Token Bearer Session Confirmed for {me_data['email']} (Verified: {me_data['is_verified']})")

print("\n==================================================")
print("🎉 All Backend Endpoints & PostGIS Integrations Verified!")
print("==================================================")
