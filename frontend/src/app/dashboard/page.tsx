"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { UserDashboardData } from "@/types";
import { endOwnBooking, fetchUserDashboard, logout } from "@/lib/api";

export default function UserDashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<UserDashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const res = await fetchUserDashboard();
      setData(res);
    } catch (err: any) {
      if (err.message === "UNAUTHORIZED") {
        router.replace("/login");
        return;
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleEnd = async (id: number) => {
    await endOwnBooking(id);
    await load();
  };

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  if (loading || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-xs font-bold text-slate-500">
        Verifying session...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link href="/" className="px-3.5 py-1.5 rounded-full bg-[#FFCA20] text-[#111827] font-black text-base">
              parkkaro
            </Link>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-black uppercase">
              User Dashboard
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs font-bold">
            {data.user.role === "developer" && (
              <Link href="/dev-dashboard" className="px-3 py-1.5 rounded-xl bg-[#1C4178] text-white">
                Dev Console
              </Link>
            )}
            <Link href="/" className="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700">
              Live Map
            </Link>
            <button onClick={handleLogout} className="px-3 py-1.5 rounded-xl bg-rose-50 text-rose-700 border border-rose-200">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        <section className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-[11px] font-black uppercase tracking-wider text-[#1C4178]">Signed in account</p>
            <h1 className="text-2xl font-black mt-0.5">{data.user.full_name || data.user.email}</h1>
            <p className="text-xs text-slate-500 mt-1">
              {data.user.email} • Role: {data.user.role}
            </p>
          </div>
          <Link href="/" className="px-5 py-2.5 rounded-2xl bg-[#FFCA20] text-[#111827] font-black text-xs shadow-sm">
            Find &amp; Book Parking
          </Link>
        </section>

        <section className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-[10px] font-bold uppercase text-slate-500">Total Bookings</p>
            <p className="text-2xl font-black text-[#1C4178] mt-1">{data.summary.total_bookings}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-[10px] font-bold uppercase text-slate-500">Active Sessions</p>
            <p className="text-2xl font-black text-emerald-600 mt-1">{data.summary.active_bookings}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-[10px] font-bold uppercase text-slate-500">Past Sessions</p>
            <p className="text-2xl font-black text-slate-700 mt-1">{data.summary.completed_or_past}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-[10px] font-bold uppercase text-slate-500">Total Parking Fees</p>
            <p className="text-2xl font-black text-slate-900 mt-1">₹{data.summary.total_spent}</p>
          </div>
        </section>

        <section className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-black">Your Parking Bookings</h2>
            <button onClick={load} className="px-3 py-1.5 rounded-xl bg-slate-100 text-xs font-bold text-slate-700">
              Refresh
            </button>
          </div>
          {data.bookings.length === 0 ? (
            <p className="text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
              No personal bookings yet.
            </p>
          ) : (
            <div className="space-y-3">
              {data.bookings.map((b) => (
                <div
                  key={b.id}
                  className="p-4 rounded-2xl border border-slate-200 bg-slate-50 flex flex-wrap items-center justify-between gap-3"
                >
                  <div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="font-black text-[#1C4178] uppercase">{b.city}</span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-white border border-slate-200">
                        {b.status}
                      </span>
                      <span className="text-slate-500 uppercase">{b.vehicle_type}</span>
                    </div>
                    <p className="font-black text-sm mt-1">{b.spot_name || "Parking Spot"}</p>
                    <p className="text-[11px] text-slate-500">
                      {b.user_name} • Ends {new Date(b.end_time).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-black text-sm">
                      {b.total_cost && b.total_cost > 0 ? `₹${b.total_cost}` : "FREE"}
                    </span>
                    {b.status === "active" && (
                      <button
                        onClick={() => handleEnd(b.id)}
                        className="px-3 py-1.5 rounded-xl bg-rose-500 text-white text-xs font-bold"
                      >
                        End Park
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
