"use client";

import React from "react";
import Link from "next/link";
import { ShieldCheck, Car, Database, Sparkles, LogIn } from "lucide-react";

interface NavbarProps {
  selectedCity: string;
  onSelectCity: (city: string) => void;
  availableCities: string[];
  backendStatus: "connected" | "connecting" | "error";
  totalSpots: number;
}

export default function Navbar({
  selectedCity,
  onSelectCity,
  availableCities,
  backendStatus,
  totalSpots,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Car className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-xl font-black tracking-tight text-slate-900">
                Park<span className="text-blue-600">Karo</span>
              </span>
              <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wider">
                Live Test
              </span>
            </div>
            <p className="text-[11px] text-slate-500 -mt-0.5">Find • Check • Park</p>
          </div>
        </div>

        {/* City Filter Tabs */}
        <div className="hidden md:flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
          <button
            onClick={() => onSelectCity("All")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedCity === "All"
                ? "bg-white text-blue-600 shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            All Cities ({totalSpots})
          </button>
          {availableCities.map((city) => (
            <button
              key={city}
              onClick={() => onSelectCity(city)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedCity === city
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {city}
            </button>
          ))}
        </div>

        {/* Supabase & Backend Status + Account */}
        <div className="flex items-center space-x-2">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-colors"
          >
            <LogIn className="w-3.5 h-3.5 text-[#FFCA20]" />
            <span>Sign In</span>
          </Link>
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
              backendStatus === "connected"
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : backendStatus === "connecting"
                ? "bg-amber-50 text-amber-700 border-amber-200 animate-pulse"
                : "bg-rose-50 text-rose-700 border-rose-200"
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span className="font-semibold">
              {backendStatus === "connected"
                ? "Supabase + FastAPI"
                : backendStatus === "connecting"
                ? "Connecting..."
                : "Offline"}
            </span>
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "connected"
                  ? "bg-emerald-500"
                  : backendStatus === "connecting"
                  ? "bg-amber-500"
                  : "bg-rose-500"
              }`}
            />
          </div>
        </div>
      </div>
    </header>
  );
}
