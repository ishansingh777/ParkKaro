"use client";

import React from "react";
import { ParkingSpot } from "../types";
import { MapPin, Car, Bike, AlertTriangle, CheckCircle2, IndianRupee, Navigation } from "lucide-react";

interface SpotCardProps {
  spot: ParkingSpot;
  isSelected: boolean;
  onSelect: (spot: ParkingSpot) => void;
  onBook: (spot: ParkingSpot) => void;
}

export default function SpotCard({ spot, isSelected, onSelect, onBook }: SpotCardProps) {
  const isNoParking = spot.rule_type === "NO_PARKING";
  const isPaid = spot.is_paid;
  const isAllowed = spot.rule_type === "ALLOWED";

  return (
    <div
      onClick={() => onSelect(spot)}
      className={`group relative rounded-2xl border transition-all duration-200 p-4 cursor-pointer ${
        isSelected
          ? "border-blue-500 bg-blue-50/50 shadow-md ring-2 ring-blue-500/20"
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
      <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-3">
        <MapPin className="w-3.5 h-3.5 shrink-0 text-slate-400" />
        <span className="truncate">{spot.address || "Main Street"}</span>
      </div>

      {/* Rule Description */}
      {spot.rule_description && (
        <p className="text-xs text-slate-600 bg-slate-50 rounded-lg p-2 mb-3 border border-slate-100 italic">
          "{spot.rule_description}"
        </p>
      )}

      {/* Slots Info */}
      {!isNoParking ? (
        <div className="grid grid-cols-2 gap-2 mb-3">
          {/* Car Slots */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-2.5">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span className="flex items-center gap-1">
                <Car className="w-3.5 h-3.5 text-blue-600" /> Car
              </span>
              <span className="font-semibold text-slate-700">
                {spot.available_car_slots} / {spot.total_car_slots}
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
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
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-2.5">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span className="flex items-center gap-1">
                <Bike className="w-3.5 h-3.5 text-indigo-600" /> Bike
              </span>
              <span className="font-semibold text-slate-700">
                {spot.available_bike_slots} / {spot.total_bike_slots}
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div
                className="h-full rounded-full bg-emerald-500 transition-all"
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
      ) : (
        <div className="bg-rose-50 border border-rose-100 rounded-xl p-2.5 mb-3 text-xs text-rose-700 font-medium">
          ⛔ Tow-away warning active. Any parked vehicle will be fined.
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-1">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect(spot);
          }}
          className="flex-1 inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
        >
          <Navigation className="w-3.5 h-3.5" /> View on Map
        </button>

        {!isNoParking && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onBook(spot);
            }}
            disabled={spot.available_car_slots === 0 && spot.available_bike_slots === 0}
            className={`flex-1 inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold text-white transition-all shadow-sm ${
              spot.available_car_slots > 0 || spot.available_bike_slots > 0
                ? "bg-blue-600 hover:bg-blue-700 active:scale-[0.98] shadow-blue-500/20"
                : "bg-slate-300 cursor-not-allowed"
            }`}
          >
            {spot.available_car_slots > 0 || spot.available_bike_slots > 0
              ? "Book Slot"
              : "Full"}
          </button>
        )}
      </div>
    </div>
  );
}
