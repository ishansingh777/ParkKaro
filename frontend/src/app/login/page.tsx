"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { fetchMe, login, signup } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const redirectByRole = (role: string) => {
    router.replace(role === "developer" ? "/dev-dashboard" : "/dashboard");
  };

  useEffect(() => {
    fetchMe()
      .then((me) => {
        if (me) redirectByRole(me.role);
      })
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const user =
        mode === "signup"
          ? await signup({ email: email.trim(), password, full_name: fullName.trim() || undefined })
          : await login({ email: email.trim(), password });
      redirectByRole(user.role);
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="px-3.5 py-1.5 rounded-full bg-[#FFCA20] text-[#111827] font-black text-base">
            parkkaro
          </Link>
          <Link href="/" className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-bold text-slate-700">
            Live Map
          </Link>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden">
          <div className="bg-[#1C4178] px-6 py-5 text-white">
            <span className="inline-block px-2.5 py-0.5 rounded-full bg-[#FFCA20] text-[#111827] text-[10px] font-black uppercase tracking-wider mb-2">
              Secure Access
            </span>
            <h1 className="text-xl font-black">Sign in to ParkKaro</h1>
            <p className="text-xs text-blue-100 mt-1">
              Access is verified against Supabase and enforced server-side.
            </p>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-2 gap-1 bg-slate-100 p-1 rounded-2xl mb-5">
              <button
                type="button"
                onClick={() => {
                  setMode("login");
                  setError(null);
                }}
                className={`py-2 rounded-xl text-xs font-black transition-all ${
                  mode === "login" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode("signup");
                  setError(null);
                }}
                className={`py-2 rounded-xl text-xs font-black transition-all ${
                  mode === "signup" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
                }`}
              >
                Create Account
              </button>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "signup" && (
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    maxLength={120}
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Rahul Sharma"
                    className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-50 border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-[#FFCA20]"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-50 border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-[#FFCA20]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Password
                </label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 8 chars (letters + numbers)"
                  className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-50 border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-[#FFCA20]"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 rounded-2xl bg-[#FFCA20] hover:bg-[#F2BC10] text-[#111827] font-black text-sm shadow-md disabled:opacity-60"
              >
                {submitting ? "Please wait..." : mode === "signup" ? "Create User Account" : "Sign In"}
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
