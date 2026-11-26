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

export interface UserProfile {
  id: number;
  email: string;
  full_name?: string | null;
  phone_number?: string | null;
  vehicle_number?: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string | null;
}

export interface AuthResponse {
  status: string;
  message: string;
  is_verified: boolean;
  user?: UserProfile | null;
  token?: string | null;
  verification_code_hint?: string | null;
}
