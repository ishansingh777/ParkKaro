"use client";

import React, { useState } from "react";
import { ParkingSpot } from "../types";
import { X, Car, Bike, Clock, IndianRupee, ShieldCheck, Check } from "lucide-react";

interface BookingModalProps {
  spot: ParkingSpot | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (bookingId: number) => void;
  apiBaseUrl: string;
}

export default function BookingModal({
  spot,
  isOpen,
  onClose,
  onSuccess,
  apiBaseUrl,
}: BookingModalProps) {
  const [userName, setUserName] = useState("");
  const [vehicleType, setVehicleType] = useState<"car" | "bike">("car");
  const [duration, setDuration] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !spot) return null;

  const totalCost = spot.is_paid ? spot.price_per_hour * duration : 0;
  const isAvailable =
    vehicleType === "car" ? spot.available_car_slots > 0 : spot.available_bike_slots > 0;

  const handleBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userName.trim()) {
      setError("Please enter your name or vehicle plate");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${apiBaseUrl}/bookings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          spot_id: spot.id,
          user_name: userName.trim(),
          vehicle_type: vehicleType,
          duration_hours: duration,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Booking failed");
      }

      const booking = await res.json();
      onSuccess(booking.id);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to complete booking");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <span className="text-[11px] font-bold text-blue-600 uppercase tracking-wider">
              Instant Live Booking
            </span>
            <h2 className="text-lg font-black text-slate-900">{spot.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-200/70 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleBooking} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-medium">
              {error}
            </div>
          )}

          {/* User Name / Plate */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Driver Name / Vehicle Plate
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Rahul Sharma or MP-09-AB-1234"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm font-medium text-slate-900 placeholder:text-slate-400"
            />
          </div>

          {/* Vehicle Type Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Select Vehicle
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setVehicleType("car")}
                className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-sm font-semibold transition-all ${
                  vehicleType === "car"
                    ? "border-blue-600 bg-blue-50 text-blue-700 shadow-sm"
                    : "border-slate-200 text-slate-600 hover:border-slate-300"
                }`}
              >
                <Car className="w-4 h-4" />
                <span>Car ({spot.available_car_slots} left)</span>
              </button>
              <button
                type="button"
                onClick={() => setVehicleType("bike")}
                className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-sm font-semibold transition-all ${
                  vehicleType === "bike"
                    ? "border-blue-600 bg-blue-50 text-blue-700 shadow-sm"
                    : "border-slate-200 text-slate-600 hover:border-slate-300"
                }`}
              >
                <Bike className="w-4 h-4" />
                <span>Bike ({spot.available_bike_slots} left)</span>
              </button>
            </div>
          </div>

          {/* Duration Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Parking Duration
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[1, 2, 3, 4].map((hrs) => (
                <button
                  key={hrs}
                  type="button"
                  onClick={() => setDuration(hrs)}
                  className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                    duration === hrs
                      ? "border-blue-600 bg-blue-600 text-white shadow-sm"
                      : "border-slate-200 text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  {hrs} {hrs === 1 ? "Hour" : "Hours"}
                </button>
              ))}
            </div>
          </div>

          {/* Pricing Summary */}
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-500" />
              <span className="text-xs text-slate-600 font-medium">
                {duration} hr @ {spot.is_paid ? `₹${spot.price_per_hour}/hr` : "Free"}
              </span>
            </div>
            <div className="flex items-center gap-1 font-extrabold text-base text-slate-900">
              {spot.is_paid ? (
                <>
                  <IndianRupee className="w-4 h-4 text-blue-600" />
                  <span>₹{totalCost}</span>
                </>
              ) : (
                <span className="text-emerald-600">FREE</span>
              )}
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || !isAvailable}
            className={`w-full py-3.5 rounded-xl font-bold text-sm text-white shadow-md transition-all ${
              isAvailable && !loading
                ? "bg-blue-600 hover:bg-blue-700 active:scale-[0.98] shadow-blue-500/25"
                : "bg-slate-300 cursor-not-allowed shadow-none"
            }`}
          >
            {loading ? "Confirming Live Slot..." : isAvailable ? `Confirm & Park Now (₹${totalCost})` : "Slot Unavailable"}
          </button>
        </form>
      </div>
    </div>
  );
}
