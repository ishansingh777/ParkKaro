export interface ParkingSpot {
  id: number;
  name: string;
  city: string;
  address: string | null;
  latitude: number;
  longitude: number;
  total_car_slots: number;
  total_bike_slots: number;
  available_car_slots: number;
  available_bike_slots: number;
  is_paid: boolean;
  price_per_hour: number;
  rule_type: "PAID" | "ALLOWED" | "NO_PARKING" | string;
  rule_description: string | null;
  distance_km?: number;
  earliest_free_time?: string | null;
}

export interface Booking {
  id: number;
  spot_id: number;
  spot_name?: string;
  city?: string;
  user_name: string;
  vehicle_type: "car" | "bike";
  start_time: string;
  end_time: string;
  status: "active" | "completed" | "cancelled";
  duration_hours?: number;
  total_cost?: number;
}

export interface RushPrediction {
  spot_id: number;
  hour: number;
  day_of_week: number;
  chance_of_full: string;
  status: "Likely available" | "Moderate rush" | "Hard to find parking";
}

export interface SignDetail {
  sign_key: string;
  name: string;
  category: string;
  meaning: string;
  wrong_meaning?: string | null;
  driver_action: string;
  parking_impact: string;
  rule_type: string;
  penalty?: string | null;
}

export interface SignScanResult {
  detected_signs: string[];
  rule_type: string;
  rule_description: string;
  sign_name?: string;
  sign_category?: string;
  sign_meaning?: string;
  wrong_meaning?: string | null;
  driver_action?: string;
  parking_impact?: string;
  penalty_info?: string | null;
  all_details?: SignDetail[];
  saved_to_db: boolean;
  spot_id?: number;
  latitude?: number;
  longitude?: number;
}

export interface AuthUser {
  id: number;
  email: string;
  full_name?: string | null;
  role: "user" | "developer" | string;
  is_active: boolean;
  created_at?: string | null;
}

export interface UserDashboardData {
  user: AuthUser;
  summary: {
    total_bookings: number;
    active_bookings: number;
    completed_or_past: number;
    total_spent: number;
  };
  bookings: Booking[];
}

export interface DevDbStatus {
  status: string;
  dialect: string;
  database_name: string;
  version: string;
  size_mb: number | null;
  active_connections: number | null;
  table_counts: Record<string, number>;
  timestamp: string;
}

export interface DevServerHealth {
  status: string;
  uptime_seconds: number;
  cpu_percent: number;
  process_memory_mb: number;
  system_memory_percent: number;
  system_memory_total_gb: number;
  models_loaded: Record<string, boolean>;
  api_latency: {
    sample_size: number;
    avg_ms: number;
    p95_ms: number;
    error_count: number;
  };
  timestamp: string;
}

export interface DevLogsResponse {
  request_logs: Array<{
    id: number;
    level: string;
    method: string;
    path: string;
    status_code: number;
    duration_ms: number;
    user_id?: number | null;
    user_role?: string | null;
    ip_address?: string | null;
    message?: string | null;
    created_at?: string | null;
  }>;
  audit_logs: Array<{
    id: number;
    actor_user_id?: number | null;
    actor_email: string;
    action: string;
    target_type?: string | null;
    target_id?: string | null;
    ip_address?: string | null;
    details?: string | null;
    created_at?: string | null;
  }>;
}

export interface DevUsersResponse {
  total: number;
  users: AuthUser[];
}
