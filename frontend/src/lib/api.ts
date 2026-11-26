import {
  ParkingSpot,
  Booking,
  RushPrediction,
  UserProfile,
  AuthResponse,
  AuthUser,
  UserDashboardData,
  DevDbStatus,
  DevServerHealth,
  DevLogsResponse,
  DevUsersResponse,
} from "@/types";

function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    return "http://localhost:8000";
  }
  return "http://127.0.0.1:8000";
}

const API_BASE_URL = getApiBaseUrl();

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
  const res = await fetch(`${API_BASE_URL}/api/bookings`, { credentials: "include" });
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
    credentials: "include",
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
    credentials: "include",
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

// ==================== Verified Driver Auth Functions ====================

export async function signUpUser(data: {
  full_name: string;
  email: string;
  phone_number?: string;
  vehicle_number?: string;
  password: string;
}): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data),
  });
  const resData = await res.json();
  if (!res.ok) throw new Error(resData.detail || "Sign up failed");
  return resData;
}

export async function verifyUserAccount(
  email: string,
  verificationCode: string
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, verification_code: verificationCode }),
  });
  const resData = await res.json();
  if (!res.ok) throw new Error(resData.detail || "Verification failed");
  return resData;
}

export async function loginUser(
  emailOrPhone: string,
  password: string
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email_or_phone: emailOrPhone, password }),
  });
  const resData = await res.json();
  if (!res.ok) throw new Error(resData.detail || "Login failed");
  return resData;
}

export async function fetchCurrentUser(token?: string): Promise<UserProfile> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers,
    credentials: "include",
  });
  if (!res.ok) throw new Error("Session invalid or expired");
  return res.json();
}

// ==================== RBAC & Dashboard Functions ====================

export async function signup(payload: {
  email: string;
  password: string;
  full_name?: string;
}): Promise<AuthUser> {
  const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Signup failed");
  return data;
}

export async function login(payload: { email: string; password: string }): Promise<AuthUser> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Invalid credentials");
  return data;
}

export async function logout(): Promise<void> {
  await fetch(`${API_BASE_URL}/api/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export async function fetchMe(): Promise<AuthUser | null> {
  const res = await fetch(`${API_BASE_URL}/api/auth/me`, { credentials: "include" });
  if (res.status === 401) return null;
  if (!res.ok) throw new Error("Failed to load session");
  return res.json();
}

export async function fetchUserDashboard(): Promise<UserDashboardData> {
  const res = await fetch(`${API_BASE_URL}/api/user/dashboard`, { credentials: "include" });
  if (res.status === 401) throw new Error("UNAUTHORIZED");
  if (!res.ok) throw new Error("Failed to load user dashboard");
  return res.json();
}

export async function endOwnBooking(bookingId: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/user/bookings/${bookingId}/end`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) throw new Error("Failed to end booking");
}

export async function fetchDevDbStatus(): Promise<DevDbStatus> {
  const res = await fetch(`${API_BASE_URL}/api/dev/db-status`, { credentials: "include" });
  if (res.status === 401) throw new Error("UNAUTHORIZED");
  if (res.status === 403) throw new Error("FORBIDDEN");
  if (!res.ok) throw new Error("Failed to load database status");
  return res.json();
}

export async function fetchDevHealth(): Promise<DevServerHealth> {
  const res = await fetch(`${API_BASE_URL}/api/dev/health`, { credentials: "include" });
  if (res.status === 401) throw new Error("UNAUTHORIZED");
  if (res.status === 403) throw new Error("FORBIDDEN");
  if (!res.ok) throw new Error("Failed to load server health");
  return res.json();
}

export async function fetchDevLogs(level?: string): Promise<DevLogsResponse> {
  const url = level
    ? `${API_BASE_URL}/api/dev/logs?level=${encodeURIComponent(level)}`
    : `${API_BASE_URL}/api/dev/logs`;
  const res = await fetch(url, { credentials: "include" });
  if (res.status === 401) throw new Error("UNAUTHORIZED");
  if (res.status === 403) throw new Error("FORBIDDEN");
  if (!res.ok) throw new Error("Failed to load logs");
  return res.json();
}

export async function fetchDevUsers(): Promise<DevUsersResponse> {
  const res = await fetch(`${API_BASE_URL}/api/dev/users`, { credentials: "include" });
  if (res.status === 401) throw new Error("UNAUTHORIZED");
  if (res.status === 403) throw new Error("FORBIDDEN");
  if (!res.ok) throw new Error("Failed to load users");
  return res.json();
}

export async function toggleDevUserStatus(userId: number, isActive: boolean): Promise<AuthUser> {
  const res = await fetch(`${API_BASE_URL}/api/dev/users/${userId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ is_active: isActive }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Failed to update user status");
  return data;
}
