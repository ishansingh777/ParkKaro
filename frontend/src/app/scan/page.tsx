"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import { scanSign } from "@/lib/api";
import { SignScanResult } from "@/types";
import {
  Camera,
  Upload,
  ArrowLeft,
  CheckCircle,
  AlertOctagon,
  Sparkles,
  MapPin,
  RefreshCw,
} from "lucide-react";

export default function SignScannerPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SignScanResult | null>(null);
  const [gpsCoords, setGpsCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [gpsStatus, setGpsStatus] = useState<string>("Detecting GPS location...");
  const fileInputRef = useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGpsCoords({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          });
          setGpsStatus(`GPS Acquired: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`);
        },
        (err) => {
          console.warn("GPS error:", err.message);
          // Fallback location: Indore center
          setGpsCoords({ latitude: 22.7196, longitude: 75.8577 });
          setGpsStatus("Default location set (Indore)");
        }
      );
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleScan = async () => {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const res = await scanSign(selectedFile, gpsCoords || undefined);
      setResult(res);
    } catch (err: any) {
      alert(`Scanning failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Top Bar */}
      <header className="p-4 flex items-center justify-between border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-20">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Map
        </Link>
        <span className="font-extrabold text-blue-400 flex items-center gap-1.5 text-sm">
          <Sparkles className="w-4 h-4 text-amber-400" /> YOLOv8 Sign Scanner
        </span>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-lg w-full mx-auto p-4 flex flex-col justify-between">
        <div className="flex flex-col gap-4">
          <div className="text-center py-2">
            <h1 className="text-2xl font-black text-white">Scan Parking Board</h1>
            <p className="text-xs text-slate-400 mt-1">
              Capture or upload any Indian parking / tow-away sign to instantly detect rules and enrich the map.
            </p>
            <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 text-[11px] text-slate-300">
              <MapPin className="w-3.5 h-3.5 text-emerald-400" />
              {gpsStatus}
            </div>
          </div>

          {/* Camera Viewport / Preview Box */}
          <div className="relative aspect-[4/3] rounded-3xl overflow-hidden bg-slate-950 border-2 border-dashed border-slate-700 flex flex-col items-center justify-center p-4">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Captured Parking Sign"
                className="w-full h-full object-contain rounded-2xl"
              />
            ) : (
              <div className="text-center flex flex-col items-center gap-3 text-slate-400">
                <div className="w-16 h-16 rounded-full bg-slate-800/80 flex items-center justify-center text-blue-400">
                  <Camera className="w-8 h-8" />
                </div>
                <p className="text-xs max-w-xs font-medium">
                  Point your camera at "No Parking", "Paid Parking", or "Tow Zone" signs.
                </p>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 py-3 px-4 rounded-2xl bg-slate-800 hover:bg-slate-700 font-bold text-sm text-slate-200 border border-slate-700 flex items-center justify-center gap-2 transition-all"
            >
              <Upload className="w-4 h-4" /> Choose / Retake
            </button>

            <button
              onClick={handleScan}
              disabled={!selectedFile || loading}
              className={`flex-1 py-3 px-4 rounded-2xl font-bold text-sm text-white flex items-center justify-center gap-2 shadow-lg transition-all ${
                !selectedFile || loading
                  ? "bg-blue-600/50 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-500 shadow-blue-500/25 hover:scale-[1.02]"
              }`}
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" /> Run Sign AI
                </>
              )}
            </button>
          </div>

          {/* Results Card */}
          {result && (
            <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700 shadow-xl flex flex-col gap-3 animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">Detection Result</span>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                    result.rule_type === "NO_PARKING"
                      ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                      : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                  }`}
                >
                  {result.rule_type}
                </span>
              </div>

              <div className="flex items-start gap-3">
                {result.rule_type === "NO_PARKING" ? (
                  <AlertOctagon className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
                )}
                <div>
                  <h4 className="font-bold text-base text-white">
                    {result.detected_signs.join(", ") || "Parking Board Identified"}
                  </h4>
                  <p className="text-xs text-slate-300 mt-1">
                    {result.rule_description}
                  </p>
                </div>
              </div>

              {result.saved_to_db && (
                <div className="text-[11px] text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 rounded-xl p-2 flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 shrink-0" />
                  <span>
                    Smart Feedback Loop: Spot & GPS rule saved into PostGIS database automatically!
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
