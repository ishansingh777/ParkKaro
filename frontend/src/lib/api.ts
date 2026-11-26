import { ParkingSpot, Booking, RushPrediction, SignScanResult } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  if (!res.ok) throw new Error("Backend unavailable");
  return res.json();
}

export async function fetchSpots(city?: string): Promise<ParkingSpot[]> {
  const url = city && city !== "All"
    ? `${API_BASE_URL}/api/spots?city=${encodeURIComponent(city)}`
    : `${API_BASE_URL}/api/spots`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch spots");
  return res.json();
}

export async function fetchSpotById(spotId: number): Promise<ParkingSpot> {
  const res = await fetch(`${API_BASE_URL}/api/spots/${spotId}`);
  if (!res.ok) throw new Error("Spot not found");
  return res.json();
}

export async function fetchNearestSpots(
  lat: number,
  lng: number,
  vehicleType: "car" | "bike" = "car",
  limit: number = 3
): Promise<ParkingSpot[]> {
  const res = await fetch(
    `${API_BASE_URL}/api/nearest?latitude=${lat}&longitude=${lng}&vehicle_type=${vehicleType}&limit=${limit}`
  );
  if (!res.ok) throw new Error("Failed to fetch nearest spots");
  return res.json();
}

export async function fetchActiveBookings(): Promise<Booking[]> {
  const res = await fetch(`${API_BASE_URL}/api/bookings`);
  if (!res.ok) throw new Error("Failed to fetch bookings");
  return res.json();
}

export async function createBooking(data: {
  spot_id: number;
  user_name: string;
  vehicle_type: "car" | "bike";
  duration_hours: number;
}): Promise<Booking> {
  const res = await fetch(`${API_BASE_URL}/api/book`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Booking failed" }));
    throw new Error(error.detail || "Booking failed");
  }
  return res.json();
}

export async function endBooking(bookingId: number): Promise<{ message: string; status: string }> {
  const res = await fetch(`${API_BASE_URL}/api/bookings/${bookingId}/end`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to end booking");
  return res.json();
}

export async function predictRush(
  spotId: number,
  hour: number,
  dayOfWeek: number
): Promise<RushPrediction> {
  const res = await fetch(
    `${API_BASE_URL}/api/predict-rush?spot_id=${spotId}&hour=${hour}&day_of_week=${dayOfWeek}`
  );
  if (!res.ok) throw new Error("Failed to predict rush");
  return res.json();
}

export async function scanSign(
  file: File,
  coords?: { latitude: number; longitude: number }
): Promise<SignScanResult> {
  const formData = new FormData();
  formData.append("file", file);
  if (coords) {
    formData.append("latitude", coords.latitude.toString());
    formData.append("longitude", coords.longitude.toString());
  }

  const res = await fetch(`${API_BASE_URL}/api/scan-sign`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Sign scanning failed" }));
    throw new Error(error.detail || "Sign scanning failed");
  }
  return res.json();
}
