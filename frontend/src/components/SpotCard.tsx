"use client";

import React from "react";
import { ParkingSpot } from "../types";
import RushBadge from "./RushBadge";
import {
  MapPin,
  Car,
  Bike,
  AlertTriangle,
  CheckCircle2,
  IndianRupee,
  Navigation,
  Clock,
} from "lucide-react";

interface SpotCardProps {
  spot: ParkingSpot;
  isSelected: boolean;
  vehicleType?: "car" | "bike";
  onSelect: (spot: ParkingSpot) => void;
  onBook: (spot: ParkingSpot) => void;
  onFindNearest?: (spot: ParkingSpot) => void;
}

export default function SpotCard({
  spot,
  isSelected,
  vehicleType = "car",
  onSelect,
  onBook,
  onFindNearest,
}: SpotCardProps) {
  const isNoParking = spot.rule_type === "NO_PARKING";
  const isPaid = spot.is_paid;

  const availableSlots =
    vehicleType === "car" ? spot.available_car_slots : spot.available_bike_slots;
  const totalSlots =
    vehicleType === "car" ? spot.total_car_slots : spot.total_bike_slots;
  const isFull = !isNoParking && availableSlots <= 0;

  return (
    <div
      onClick={() => onSelect(spot)}
      className={`group relative rounded-2xl border transition-all duration-200 p-4 cursor-pointer ${
        isSelected
          ? "border-blue-500 bg-blue-50/40 shadow-md ring-2 ring-blue-500/20"
          : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
      }`}
    >
      {/* Header & Badges */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            {spot.city}
          </span>
          <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
            {spot.name}
          </h3>
        </div>

        {/* Rule Badge */}
        {isNoParking ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-700 border border-rose-200">
            <AlertTriangle className="w-3.5 h-3.5" />
            No Parking
          </span>
        ) : isFull ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-700 border border-rose-200 animate-pulse">
            <Clock className="w-3.5 h-3.5" />
            Full {spot.earliest_free_time ? `(${spot.earliest_free_time})` : ""}
          </span>
        ) : isPaid ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-200">
            <IndianRupee className="w-3 h-3" />
            ₹{spot.price_per_hour}/hr
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Free Parking
          </span>
        )}
      </div>

      {/* Address */}
      <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-2">
        <MapPin className="w-3.5 h-3.5 shrink-0 text-slate-400" />
        <span className="truncate">{spot.address || "Main Street"}</span>
      </div>

      {/* Rule Description */}
      {spot.rule_description && (
        <p className="text-xs text-slate-600 bg-slate-50 rounded-lg p-2 mb-3 border border-slate-100 italic">
          "{spot.rule_description}"
        </p>
      )}

      {/* Slots Info: 2W vs 4W */}
      {!isNoParking && (
        <div className="grid grid-cols-2 gap-2 mb-3">
          {/* Car Slots */}
          <div
            className={`p-2 rounded-xl border text-xs ${
              vehicleType === "car"
                ? "bg-blue-50/70 border-blue-200 ring-1 ring-blue-300"
                : "bg-slate-50 border-slate-100 text-slate-500"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="flex items-center gap-1 font-medium">
                <Car className="w-3.5 h-3.5 text-blue-600" /> Car Slots
              </span>
              <span className="font-bold text-slate-800">
                {spot.available_car_slots} / {spot.total_car_slots}
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  spot.available_car_slots > 3 ? "bg-emerald-500" : "bg-amber-500"
                }`}
                style={{
                  width: `${
                    spot.total_car_slots > 0
                      ? (spot.available_car_slots / spot.total_car_slots) * 100
                      : 0
                  }%`,
                }}
              />
            </div>
          </div>

          {/* Bike Slots */}
          <div
            className={`p-2 rounded-xl border text-xs ${
              vehicleType === "bike"
                ? "bg-emerald-50/70 border-emerald-200 ring-1 ring-emerald-300"
                : "bg-slate-50 border-slate-100 text-slate-500"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="flex items-center gap-1 font-medium">
                <Bike className="w-3.5 h-3.5 text-emerald-600" /> Bike Slots
              </span>
              <span className="font-bold text-slate-800">
                {spot.available_bike_slots} / {spot.total_bike_slots}
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  spot.available_bike_slots > 3 ? "bg-emerald-500" : "bg-amber-500"
                }`}
                style={{
                  width: `${
                    spot.total_bike_slots > 0
                      ? (spot.available_bike_slots / spot.total_bike_slots) * 100
                      : 0
                  }%`,
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* AI Rush Predictor Badge */}
      {!isNoParking && (
        <div className="mb-3">
          <RushBadge spotId={spot.id} />
        </div>
      )}

      {/* Action Footer: Book Now or Find Nearest */}
      <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-100">
        <span className="text-[11px] text-slate-400">
          Lat: {spot.latitude.toFixed(3)}, Lng: {spot.longitude.toFixed(3)}
        </span>

        {isNoParking || isFull ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (onFindNearest) onFindNearest(spot);
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-all"
          >
            <Navigation className="w-3.5 h-3.5 text-blue-600" />
            Find Nearest
          </button>
        ) : (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onBook(spot);
            }}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-sm shadow-blue-500/20 transition-all hover:scale-[1.02]"
          >
            Book Slot
          </button>
        )}
      </div>
    </div>
  );
}
