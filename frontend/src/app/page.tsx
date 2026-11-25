"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { ParkingSpot, Booking } from "@/types";
import { fetchSpots, fetchActiveBookings, fetchHealth, endBooking, fetchNearestSpots } from "@/lib/api";
import Navbar from "@/components/Navbar";
import SpotCard from "@/components/SpotCard";
import BookingModal from "@/components/BookingModal";
import ActiveSessions from "@/components/ActiveSessions";
import {
  Car,
  Bike,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Navigation,
  Compass,
} from "lucide-react";

// Dynamically import ParkingMap with SSR disabled (Leaflet requires browser window)
const ParkingMap = dynamic(() => import("@/components/ParkingMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[520px] lg:h-[680px] rounded-3xl bg-slate-100 flex items-center justify-center border border-slate-200 text-slate-400">
      <div className="flex flex-col items-center gap-2">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-semibold">Loading Live OpenStreetMap...</span>
      </div>
    </div>
  ),
});

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [spots, setSpots] = useState<ParkingSpot[]>([]);
  const [activeBookings, setActiveBookings] = useState<Booking[]>([]);
  const [selectedCity, setSelectedCity] = useState<string>("All");
  const [vehicleType, setVehicleType] = useState<"car" | "bike">("car");
  const [selectedSpot, setSelectedSpot] = useState<ParkingSpot | null>(null);
  const [bookingSpot, setBookingSpot] = useState<ParkingSpot | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState<"connected" | "connecting" | "error">("connecting");
  const [notification, setNotification] = useState<string | null>(null);

  // Fetch spots & bookings
  const loadData = async () => {
    try {
      const [spotsData, bookingsData] = await Promise.all([
        fetchSpots(selectedCity),
        fetchActiveBookings().catch(() => []),
      ]);
      setSpots(spotsData);
      setActiveBookings(bookingsData);
      setBackendStatus("connected");
    } catch (err) {
      console.error("Error fetching data:", err);
      setBackendStatus("error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [selectedCity]);

  const handleEndBooking = async (bookingId: number) => {
    try {
      await endBooking(bookingId);
      setNotification(`Parking session #${bookingId} successfully ended. Spot slot freed!`);
      loadData();
      setTimeout(() => setNotification(null), 4000);
    } catch (err: any) {
      alert(`Could not end session: ${err.message}`);
    }
  };

  const handleBookingSuccess = (bookingId: number) => {
    setNotification(`Booking #${bookingId} confirmed! Slot reserved.`);
    loadData();
    setTimeout(() => setNotification(null), 4000);
  };

  const handleFindNearest = async (spot: ParkingSpot) => {
    try {
      const nearest = await fetchNearestSpots(spot.latitude, spot.longitude, vehicleType, 3);
      if (nearest.length > 0) {
        setSelectedSpot(nearest[0]);
        setNotification(`Found nearest open alternative: ${nearest[0].name} (${nearest[0].city})`);
        setTimeout(() => setNotification(null), 5000);
      } else {
        alert("No alternate open spots found nearby.");
      }
    } catch (err: any) {
      alert(`Nearest search failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Top Navbar */}
      <Navbar
        selectedCity={selectedCity}
        onSelectCity={setSelectedCity}
        availableCities={["Indore", "Chandigarh", "Goa"]}
        backendStatus={backendStatus}
        totalSpots={spots.length}
      />

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        {/* Floating Controls Bar: 2W/4W toggle + Camera Scan + Refresh */}
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-sm">
          {/* 2-Wheeler vs 4-Wheeler Toggle */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
            <button
              onClick={() => setVehicleType("car")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                vehicleType === "car"
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Car className="w-4 h-4" /> 4-Wheeler (Car)
            </button>
            <button
              onClick={() => setVehicleType("bike")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                vehicleType === "bike"
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Bike className="w-4 h-4" /> 2-Wheeler (Bike)
            </button>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={loadData}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all shadow-sm"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
          </div>
        </div>

        {/* Toast Notification */}
        {notification && (
          <div className="mb-4 p-4 rounded-2xl bg-emerald-600 text-white shadow-lg flex items-center justify-between animate-fade-in">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <span className="font-semibold text-sm">{notification}</span>
            </div>
            <button
              onClick={() => setNotification(null)}
              className="text-emerald-200 hover:text-white font-bold text-xs"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Active Sessions Drawer */}
        <ActiveSessions bookings={activeBookings} onEndBooking={handleEndBooking} />

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Interactive Map (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-black text-slate-900">Live PostGIS Map</h2>
                <p className="text-xs text-slate-500">
                  Showing {spots.length} smart spots across {selectedCity === "All" ? "all cities" : selectedCity}
                </p>
              </div>
            </div>

            <ParkingMap
              spots={spots}
              selectedSpot={selectedSpot}
              onSelectSpot={(spot) => setSelectedSpot(spot)}
              onBookSpot={(spot) => setBookingSpot(spot)}
            />
          </div>

          {/* Parking Spots Cards (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-black text-slate-900">
                  {selectedCity === "All" ? "All Locations" : `${selectedCity} Spots`} ({spots.length})
                </h2>
                <p className="text-xs text-slate-500">
                  Showing available {vehicleType === "car" ? "Car" : "Bike"} spaces
                </p>
              </div>
            </div>

            {loading ? (
              <div className="p-8 text-center bg-white rounded-3xl border border-slate-200">
                <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                <span className="text-xs text-slate-500">Loading spots from Supabase...</span>
              </div>
            ) : spots.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-3xl border border-slate-200">
                <AlertCircle className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-semibold text-slate-700">No parking spots found.</p>
              </div>
            ) : (
              <div className="flex flex-col gap-3 max-h-[680px] overflow-y-auto pr-1">
                {spots.map((spot) => (
                  <SpotCard
                    key={spot.id}
                    spot={spot}
                    vehicleType={vehicleType}
                    isSelected={selectedSpot?.id === spot.id}
                    onSelect={(s) => setSelectedSpot(s)}
                    onBook={(s) => setBookingSpot(s)}
                    onFindNearest={handleFindNearest}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Booking Modal */}
      <BookingModal
        spot={bookingSpot}
        isOpen={!!bookingSpot}
        onClose={() => setBookingSpot(null)}
        onSuccess={handleBookingSuccess}
        apiBaseUrl={API_BASE_URL}
      />
    </div>
  );
}
