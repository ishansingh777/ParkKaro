"use client";

import React from "react";
import { Booking } from "../types";
import { Clock, CheckCircle2, Car, Bike, AlertCircle, XCircle } from "lucide-react";

interface ActiveSessionsProps {
  bookings: Booking[];
  onEndBooking: (id: number) => void;
}

export default function ActiveSessions({ bookings, onEndBooking }: ActiveSessionsProps) {
  if (bookings.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-3xl p-5 shadow-xl border border-blue-800/40 mb-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <h2 className="text-sm font-black tracking-wide uppercase text-blue-200">
            Active Parking Sessions ({bookings.length})
          </h2>
        </div>
        <span className="text-xs text-blue-300">Live PostGIS Slot Counter Active</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {bookings.map((b) => {
          const endTime = new Date(b.end_time);
          const now = new Date();
          const diffMinutes = Math.max(0, Math.round((endTime.getTime() - now.getTime()) / 60000));

          return (
            <div
              key={b.id}
              className="bg-white/10 backdrop-blur-md rounded-2xl p-3.5 border border-white/10 flex items-center justify-between"
            >
              <div>
                <div className="flex items-center gap-1.5 text-xs text-blue-200 mb-0.5">
                  {b.vehicle_type === "car" ? (
                    <Car className="w-3.5 h-3.5 text-blue-300" />
                  ) : (
                    <Bike className="w-3.5 h-3.5 text-indigo-300" />
                  )}
                  <span className="font-bold text-white uppercase">{b.user_name}</span>
                  <span>• {b.city}</span>
                </div>
                <div className="text-xs font-semibold text-slate-200 truncate max-w-[180px]">
                  {b.spot_name}
                </div>
                <div className="flex items-center gap-1 text-[11px] text-emerald-400 mt-1 font-mono">
                  <Clock className="w-3 h-3" />
                  <span>{diffMinutes} mins remaining</span>
                </div>
              </div>

              <button
                onClick={() => onEndBooking(b.id)}
                className="px-3 py-1.5 rounded-xl bg-white/20 hover:bg-rose-600 hover:border-rose-500 text-xs font-bold transition-all border border-white/20 text-white shrink-0"
              >
                End Park
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
