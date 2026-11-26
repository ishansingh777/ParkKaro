"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { DevDbStatus, DevLogsResponse, DevServerHealth, DevUsersResponse } from "@/types";
import {
  fetchDevDbStatus,
  fetchDevHealth,
  fetchDevLogs,
  fetchDevUsers,
  fetchMe,
  logout,
  toggleDevUserStatus,
} from "@/lib/api";

export default function DevDashboardPage() {
  const router = useRouter();
  const [email, setEmail] = useState<string>("");
  const [dbStatus, setDbStatus] = useState<DevDbStatus | null>(null);
  const [health, setHealth] = useState<DevServerHealth | null>(null);
  const [usersData, setUsersData] = useState<DevUsersResponse | null>(null);
  const [logsData, setLogsData] = useState<DevLogsResponse | null>(null);
  const [levelFilter, setLevelFilter] = useState<string>("");
  const [ready, setReady] = useState(false);

  const loadAll = async (level = levelFilter) => {
    try {
      const me = await fetchMe();
      if (!me) {
        router.replace("/login");
        return;
      }
      if (me.role !== "developer") {
        router.replace("/dashboard");
        return;
      }
      setEmail(me.email);

      const [db, h, u] = await Promise.all([fetchDevDbStatus(), fetchDevHealth(), fetchDevUsers()]);
      const l = await fetchDevLogs(level || undefined);
      setDbStatus(db);
      setHealth(h);
      setUsersData(u);
      setLogsData(l);
      setReady(true);
    } catch (err: any) {
      if (err.message === "UNAUTHORIZED") router.replace("/login");
      else if (err.message === "FORBIDDEN") router.replace("/dashboard");
    }
  };

  useEffect(() => {
    loadAll("");
  }, []);

  const handleToggleUser = async (userId: number, currentActive: boolean) => {
    await toggleDevUserStatus(userId, !currentActive);
    await loadAll();
  };

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-xs font-bold text-slate-500">
        Verifying developer clearance...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-[#1C4178] text-white">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link href="/" className="px-3.5 py-1.5 rounded-full bg-[#FFCA20] text-[#111827] font-black text-sm">
              parkkaro
            </Link>
            <span className="px-2.5 py-0.5 rounded-full bg-white/15 border border-white/25 text-[11px] font-black uppercase text-[#FFCA20]">
              Developer Console
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs font-bold">
            <span className="hidden sm:inline text-blue-100">{email}</span>
            <Link href="/dashboard" className="px-3 py-1.5 rounded-xl bg-white/15">
              User View
            </Link>
            <Link href="/" className="px-3 py-1.5 rounded-xl bg-white/15">
              Live Map
            </Link>
            <button onClick={handleLogout} className="px-3 py-1.5 rounded-xl bg-rose-500 text-white">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <section className="bg-white rounded-3xl border border-slate-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-black uppercase text-[#1C4178]">Supabase Database Status</h2>
              <button onClick={() => loadAll()} className="px-2.5 py-1 rounded-xl bg-slate-100 text-xs font-bold">
                Refresh
              </button>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Status</div>
                <div className="font-black mt-0.5">{dbStatus?.status}</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Size (MB)</div>
                <div className="font-black mt-0.5">{dbStatus?.size_mb ?? "N/A"}</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Users</div>
                <div className="font-black mt-0.5">{dbStatus?.table_counts.users}</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Spots</div>
                <div className="font-black mt-0.5">{dbStatus?.table_counts.parking_spots}</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Active Bookings</div>
                <div className="font-black mt-0.5">{dbStatus?.table_counts.active_bookings}</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Connections</div>
                <div className="font-black mt-0.5">{dbStatus?.active_connections ?? "N/A"}</div>
              </div>
            </div>
          </section>

          <section className="bg-white rounded-3xl border border-slate-200 p-5 shadow-sm">
            <h2 className="text-sm font-black uppercase text-[#1C4178] mb-3">Server Health &amp; Latency</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">CPU %</div>
                <div className="font-black mt-0.5">{health?.cpu_percent}%</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Process RAM</div>
                <div className="font-black mt-0.5">{health?.process_memory_mb} MB</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Uptime</div>
                <div className="font-black mt-0.5">{health?.uptime_seconds}s</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Avg Latency</div>
                <div className="font-black mt-0.5">{health?.api_latency.avg_ms} ms</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">P95 Latency</div>
                <div className="font-black mt-0.5">{health?.api_latency.p95_ms} ms</div>
              </div>
              <div className="p-2.5 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="text-[10px] font-bold uppercase text-slate-500">Errors (5xx)</div>
                <div className="font-black mt-0.5">{health?.api_latency.error_count}</div>
              </div>
            </div>
          </section>
        </div>

        <section className="bg-white rounded-3xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-sm font-black uppercase text-[#1C4178] mb-3">Registered Users</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px]">
                  <th className="py-2 pr-3">ID</th>
                  <th className="py-2 pr-3">Email</th>
                  <th className="py-2 pr-3">Name</th>
                  <th className="py-2 pr-3">Role</th>
                  <th className="py-2 pr-3">Status</th>
                  <th className="py-2 pr-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {usersData?.users.map((u) => (
                  <tr key={u.id}>
                    <td className="py-2 pr-3">{u.id}</td>
                    <td className="py-2 pr-3 font-semibold">{u.email}</td>
                    <td className="py-2 pr-3">{u.full_name || "-"}</td>
                    <td className="py-2 pr-3">{u.role}</td>
                    <td className="py-2 pr-3">{u.is_active ? "Active" : "Disabled"}</td>
                    <td className="py-2 pr-3">
                      <button
                        onClick={() => handleToggleUser(u.id, u.is_active)}
                        className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 font-bold"
                      >
                        {u.is_active ? "Disable" : "Enable"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <section className="bg-white rounded-3xl border border-slate-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-black uppercase text-[#1C4178]">Request &amp; Error Logs</h2>
              <select
                value={levelFilter}
                onChange={(e) => {
                  setLevelFilter(e.target.value);
                  loadAll(e.target.value);
                }}
                className="px-2.5 py-1 rounded-xl bg-slate-100 text-xs font-bold"
              >
                <option value="">All Levels</option>
                <option value="INFO">INFO</option>
                <option value="WARN">WARN</option>
                <option value="ERROR">ERROR</option>
              </select>
            </div>
            <div className="space-y-2 max-h-80 overflow-y-auto text-[11px] font-mono">
              {logsData?.request_logs.map((l) => (
                <div key={l.id} className="p-2 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="font-bold">
                    [{l.level}] {l.method} {l.path} → {l.status_code} ({l.duration_ms}ms)
                  </div>
                  <div className="text-slate-500">
                    role={l.user_role || "anon"} {l.message || ""}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="bg-white rounded-3xl border border-slate-200 p-5 shadow-sm">
            <h2 className="text-sm font-black uppercase text-[#1C4178] mb-3">Developer Audit Log</h2>
            <div className="space-y-2 max-h-80 overflow-y-auto text-[11px] font-mono">
              {logsData?.audit_logs.map((a) => (
                <div key={a.id} className="p-2 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="font-bold text-[#1C4178]">
                    {a.action} • {a.actor_email}
                  </div>
                  <div className="text-slate-500">{a.details || `${a.target_type || ""}:${a.target_id || ""}`}</div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
