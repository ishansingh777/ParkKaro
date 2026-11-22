"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { ParkingSpot, Booking } from "@/types";
import Navbar from "@/components/Navbar";
import SpotCard from "@/components/SpotCard";
import BookingModal from "@/components/BookingModal";
import ActiveSessions from "@/components/ActiveSessions";
import { Car, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";

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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function Home() {
  const [spots, setSpots] = useState<ParkingSpot[]>([]);
  const [activeBookings, setActiveBookings] = useState<Booking[]>([]);
  const [selectedCity, setSelectedCity] = useState<string>("All");
  const [selectedSpot, setSelectedSpot] = useState<ParkingSpot | null>(null);
  const [bookingSpot, setBookingSpot] = useState<ParkingSpot | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState<"connected" | "connecting" | "error">("connecting");
  const [notification, setNotification] = useState<string | null>(null);

  // Fetch spots & bookings
  const fetchData = async () => {
    try {
      // 1. Fetch Spots
      const url = selectedCity === "All"
        ? `${API_BASE_URL}/spots`
        : `${API_BASE_URL}/spots?city=${encodeURIComponent(selectedCity)}`;

      const [spotsRes, bookingsRes, healthRes] = await Promise.all([
        fetch(url),
        fetch(`${API_BASE_URL}/bookings`),
        fetch(`${API_BASE_URL}/health`)
      ]);

      if (spotsRes.ok && bookingsRes.ok && healthRes.ok) {
        const spotsData = await spotsRes.json();
        const bookingsData = await bookingsRes.json();
        setSpots(spotsData);
        setActiveBookings(bookingsData);
        setBackendStatus("connected");
      } else {
        setBackendStatus("error");
      }
    } catch (err) {
      console.error("Error fetching data:", err);
      setBackendStatus("error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll every 10 seconds for real-time live availability
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [selectedCity]);

  const handleEndBooking = async (bookingId: number) => {
    try {
      const res = await fetch(`${API_BASE_URL}/bookings/${bookingId}/end`, {
        method: "POST",
      });
      if (res.ok) {
        setNotification(`Parking session #${bookingId} successfully ended. Spot slot freed!`);
        fetchData();
        setTimeout(() => setNotification(null), 4000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleBookingSuccess = (bookingId: number) => {
    setNotification(`Booking #${bookingId} confirmed! Slot reserved.`);
    fetchData();
    setTimeout(() => setNotification(null), 4000);
  };

  const availableCities = Array.from(new Set(spots.map((s) => s.city)));

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Navbar */}
      <Navbar
        selectedCity={selectedCity}
        onSelectCity={setSelectedCity}
        availableCities={["Indore", "Chandigarh", "Goa"]}
        backendStatus={backendStatus}
        totalSpots={spots.length}
      />

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Toast Notification */}
        {notification && (
          <div className="mb-4 p-4 rounded-2xl bg-emerald-600 text-white shadow-lg flex items-center justify-between animate-fade-in">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-semibold text-sm">{notification}</span>
            </div>
            <button onClick={() => setNotification(null)} className="text-emerald-200 hover:text-white font-bold text-xs">
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
                  Real-time spatial spots from Supabase PostgreSQL
                </p>
              </div>

              <button
                onClick={fetchData}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-sm transition-all"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Refresh
              </button>
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
                  Live occupancy updated automatically
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
                <p className="text-sm font-semibold text-slate-700">No parking spots found for this filter.</p>
              </div>
            ) : (
              <div className="flex flex-col gap-3 max-h-[680px] overflow-y-auto pr-1">
                {spots.map((spot) => (
                  <SpotCard
                    key={spot.id}
                    spot={spot}
                    isSelected={selectedSpot?.id === spot.id}
                    onSelect={(s) => setSelectedSpot(s)}
                    onBook={(s) => setBookingSpot(s)}
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
