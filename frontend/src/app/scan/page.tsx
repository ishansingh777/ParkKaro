"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
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
  X,
  Laptop,
  Smartphone,
  Check,
  BookOpen,
  Info,
  ShieldAlert,
  AlertTriangle,
  HelpCircle,
} from "lucide-react";

export default function SignScannerPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SignScanResult | null>(null);
  const [gpsCoords, setGpsCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [gpsStatus, setGpsStatus] = useState<string>("Detecting GPS location...");

  // Camera & Device states
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [availableDevices, setAvailableDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>("");
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  const fileUploadInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // Helper to identify if a camera is the laptop's built-in webcam
  const isLaptopWebcam = (label: string) => {
    const l = label.toLowerCase();
    const isPhone = l.includes("phone") || l.includes("link") || l.includes("droidcam") || l.includes("iriun");
    if (isPhone) return false;
    return (
      l.includes("integrated") ||
      l.includes("webcam") ||
      l.includes("internal") ||
      l.includes("builtin") ||
      l.includes("front") ||
      l.includes("camera") ||
      l.includes("facetime") ||
      l.includes("realtek") ||
      l.includes("chicony") ||
      l.includes("sunplus")
    );
  };

  // Enumerate all camera devices available on the system
  const refreshCameraDevices = useCallback(async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = devices.filter((d) => d.kind === "videoinput");
      setAvailableDevices(videoInputs);

      // Select default device (laptop webcam prioritized over phone)
      if (videoInputs.length > 0 && !selectedDeviceId) {
        const laptopCam = videoInputs.find((d) => isLaptopWebcam(d.label));
        if (laptopCam) {
          setSelectedDeviceId(laptopCam.deviceId);
        } else {
          // If no label matched laptop specifically, avoid phone-link if possible
          const nonPhoneCam = videoInputs.find(
            (d) => !d.label.toLowerCase().includes("phone") && !d.label.toLowerCase().includes("link")
          );
          setSelectedDeviceId(nonPhoneCam ? nonPhoneCam.deviceId : videoInputs[0].deviceId);
        }
      }
    } catch (err) {
      console.warn("Could not enumerate camera devices:", err);
    }
  }, [selectedDeviceId]);

  // GPS Acquisition
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGpsCoords({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          });
          setGpsStatus(`GPS: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`);
        },
        (err) => {
          console.warn("GPS error:", err.message);
          setGpsCoords({ latitude: 22.7196, longitude: 75.8577 });
          setGpsStatus("Default location set (Indore)");
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    }
    refreshCameraDevices();
  }, [refreshCameraDevices]);

  // Stop camera stream safely
  const stopCamera = useCallback(() => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  // Start live camera stream (defaults to laptop webcam, avoiding phone link)
  const startCamera = async (targetDeviceId?: string) => {
    setCameraError(null);
    setResult(null);
    setSelectedFile(null);
    setPreviewUrl(null);

    // Stop existing stream if running
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Live camera stream is not supported in this browser.");
      }

      const deviceIdToUse = targetDeviceId || selectedDeviceId;

      // Crucial: Laptop webcam is front-facing ("user"), while phones are "environment".
      // Specifying deviceId (if available) or facingMode: "user" guarantees the laptop webcam opens!
      const videoConstraints: MediaTrackConstraints = deviceIdToUse
        ? {
            deviceId: { exact: deviceIdToUse },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          }
        : {
            facingMode: "user", // Laptop built-in webcam
            width: { ideal: 1280 },
            height: { ideal: 720 },
          };

      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints,
        audio: false,
      });

      mediaStreamRef.current = stream;
      setIsCameraActive(true);

      // Once permission is granted, device labels are fully populated by browser
      await refreshCameraDevices();

      // Update current selected deviceId based on active track
      const activeTrack = stream.getVideoTracks()[0];
      if (activeTrack) {
        const settings = activeTrack.getSettings();
        if (settings.deviceId) {
          setSelectedDeviceId(settings.deviceId);
        }
      }

      // Attach stream to video tag
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch((err) => {
            console.warn("Video play error:", err);
          });
        }
      }, 100);
    } catch (err: any) {
      console.warn("Camera start error:", err);
      stopCamera();
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setCameraError(
          "Camera permission was blocked. Please click the camera icon in your browser address bar to allow laptop webcam access, or use the 'Upload Image' option."
        );
      } else {
        setCameraError(
          `Could not open laptop webcam: ${err.message || "Device unavailable"}. You can still upload images.`
        );
      }
    }
  };

  // Switch camera when user picks from dropdown
  const handleDeviceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newDeviceId = e.target.value;
    setSelectedDeviceId(newDeviceId);
    startCamera(newDeviceId);
  };

  // Capture still image from the laptop camera feed
  const capturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, width, height);
    canvas.toBlob(
      (blob) => {
        if (blob) {
          const file = new File([blob], `laptop_camera_scan_${Date.now()}.jpg`, {
            type: "image/jpeg",
          });
          setSelectedFile(file);
          setPreviewUrl(URL.createObjectURL(blob));
          stopCamera();
        }
      },
      "image/jpeg",
      0.92
    );
  };

  // Handle image upload from computer files/gallery
  const handleFileSelected = (file: File) => {
    stopCamera();
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setCameraError(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
    e.target.value = "";
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("image/")) {
        handleFileSelected(file);
      } else {
        alert("Please drop a valid image file (JPEG, PNG, WebP).");
      }
    }
  };

  // Run AI analysis with YOLOv8 backend
  const handleScan = async () => {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const res = await scanSign(selectedFile, gpsCoords || undefined);
      setResult(res);
    } catch (err: any) {
      alert(`Sign scanner failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Reset to initial choice state
  const handleReset = () => {
    stopCamera();
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setCameraError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Header */}
      <header className="p-4 flex items-center justify-between border-b border-slate-800/80 bg-slate-900/80 backdrop-blur sticky top-0 z-30">
        <Link
          href="/"
          onClick={stopCamera}
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Map
        </Link>
        <span className="font-extrabold text-blue-400 flex items-center gap-1.5 text-sm">
          <Sparkles className="w-4 h-4 text-amber-400" /> YOLOv8 Sign Scanner
        </span>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-lg w-full mx-auto p-4 sm:p-6 flex flex-col justify-between">
        <div className="flex flex-col gap-4">
          {/* Header Title */}
          <div className="text-center py-1">
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Check Parking Sign
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-sm mx-auto">
              Open your laptop webcam or upload an image to verify parking rules and tow-away zones with AI.
            </p>
            <div className="mt-2.5 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-300 shadow-sm">
              <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>{gpsStatus}</span>
            </div>
          </div>

          {/* Camera Error Alert if permission blocked */}
          {cameraError && (
            <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start justify-between gap-2">
              <span className="leading-relaxed">{cameraError}</span>
              <button
                onClick={() => setCameraError(null)}
                className="p-1 hover:text-white shrink-0"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Viewport Box */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative aspect-[4/3] rounded-3xl overflow-hidden bg-slate-900 border-2 transition-all flex flex-col items-center justify-center ${
              isDragOver
                ? "border-blue-500 bg-blue-950/20 shadow-lg shadow-blue-500/10 scale-[1.01]"
                : "border-slate-800"
            }`}
          >
            {/* Mode 1: Live Laptop Webcam Stream */}
            {isCameraActive ? (
              <div className="relative w-full h-full bg-black flex items-center justify-center">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />

                {/* Animated Scanner Reticle / Target Box */}
                <div className="absolute inset-8 border border-blue-400/40 rounded-2xl pointer-events-none flex items-center justify-center">
                  <div className="w-full h-0.5 bg-gradient-to-r from-transparent via-blue-400 to-transparent animate-pulse" />
                  <div className="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2 border-blue-400" />
                  <div className="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2 border-blue-400" />
                  <div className="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2 border-blue-400" />
                  <div className="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2 border-blue-400" />
                </div>

                {/* Top Overlay: Camera Selection Dropdown & Close */}
                <div className="absolute top-3 inset-x-3 flex items-center justify-between pointer-events-auto">
                  {/* Camera Selector Dropdown (Allows switching to laptop webcam or phone) */}
                  {availableDevices.length > 1 ? (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-950/80 backdrop-blur border border-slate-700 text-xs">
                      <Laptop className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                      <select
                        value={selectedDeviceId}
                        onChange={handleDeviceChange}
                        className="bg-transparent text-white text-[11px] font-semibold outline-none cursor-pointer max-w-[170px] truncate"
                      >
                        {availableDevices.map((dev, idx) => (
                          <option
                            key={dev.deviceId}
                            value={dev.deviceId}
                            className="bg-slate-900 text-white"
                          >
                            {dev.label
                              ? isLaptopWebcam(dev.label)
                                ? `💻 ${dev.label}`
                                : `📱 ${dev.label}`
                              : `Camera ${idx + 1}`}
                          </option>
                        ))}
                      </select>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-950/80 backdrop-blur border border-slate-700 text-[11px] text-blue-300 font-semibold">
                      <Laptop className="w-3.5 h-3.5 text-blue-400" /> Laptop Webcam
                    </div>
                  )}

                  <button
                    onClick={stopCamera}
                    title="Close Camera"
                    className="p-1.5 rounded-full bg-slate-950/80 text-white hover:bg-slate-800 backdrop-blur border border-slate-700 shadow"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Bottom Overlay: Shutter Button */}
                <div className="absolute bottom-4 inset-x-0 flex items-center justify-center">
                  <button
                    onClick={capturePhoto}
                    className="w-16 h-16 rounded-full bg-white border-4 border-blue-600 shadow-2xl flex items-center justify-center text-blue-600 hover:scale-105 active:scale-95 transition-transform"
                    title="Capture Photo"
                  >
                    <Camera className="w-7 h-7" />
                  </button>
                </div>
              </div>
            ) : previewUrl ? (
              /* Mode 2: Captured/Uploaded Photo Preview */
              <div className="relative w-full h-full p-2 bg-slate-950 flex items-center justify-center">
                <img
                  src={previewUrl}
                  alt="Captured Parking Sign"
                  className="w-full h-full object-contain rounded-2xl"
                />
                <button
                  onClick={handleReset}
                  title="Remove Image"
                  className="absolute top-4 right-4 p-2 rounded-full bg-slate-900/90 text-white hover:bg-rose-600 transition-colors border border-slate-700 shadow-md"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              /* Mode 3: Two Clear Options (Laptop Camera vs Upload) */
              <div className="w-full h-full p-6 flex flex-col items-center justify-center text-center">
                <div className="grid grid-cols-2 gap-3.5 w-full max-w-sm">
                  {/* Option 1: Open Laptop Webcam */}
                  <button
                    type="button"
                    onClick={() => startCamera()}
                    className="group flex flex-col items-center justify-center p-4 rounded-2xl bg-gradient-to-b from-slate-800/90 to-slate-900 border border-slate-700/80 hover:border-blue-500 hover:from-blue-950/30 hover:to-slate-900 transition-all shadow-md active:scale-95"
                  >
                    <div className="w-12 h-12 rounded-2xl bg-blue-600/20 text-blue-400 group-hover:bg-blue-600 group-hover:text-white flex items-center justify-center mb-2.5 transition-colors">
                      <Laptop className="w-6 h-6" />
                    </div>
                    <span className="font-bold text-sm text-white group-hover:text-blue-300">
                      Laptop Camera
                    </span>
                    <span className="text-[11px] text-slate-400 mt-0.5 text-center leading-tight">
                      Use built-in webcam
                    </span>
                  </button>

                  {/* Option 2: Upload Image from Laptop */}
                  <button
                    type="button"
                    onClick={() => fileUploadInputRef.current?.click()}
                    className="group flex flex-col items-center justify-center p-4 rounded-2xl bg-gradient-to-b from-slate-800/90 to-slate-900 border border-slate-700/80 hover:border-indigo-500 hover:from-indigo-950/30 hover:to-slate-900 transition-all shadow-md active:scale-95"
                  >
                    <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white flex items-center justify-center mb-2.5 transition-colors">
                      <Upload className="w-6 h-6" />
                    </div>
                    <span className="font-bold text-sm text-white group-hover:text-indigo-300">
                      Upload Image
                    </span>
                    <span className="text-[11px] text-slate-400 mt-0.5 text-center leading-tight">
                      Browse laptop files
                    </span>
                  </button>
                </div>

                {/* Multiple Cameras Detected Hint */}
                {availableDevices.length > 1 && (
                  <div className="mt-3 flex items-center gap-1.5 text-[11px] text-slate-400 bg-slate-900/80 px-3 py-1 rounded-full border border-slate-800">
                    <Laptop className="w-3 h-3 text-blue-400 shrink-0" />
                    <span>Laptop webcam selected by default ({availableDevices.length} cameras found)</span>
                  </div>
                )}

                <p className="text-[11px] text-slate-500 mt-3">
                  Drag & drop any photo here, or select an option above
                </p>
              </div>
            )}

            {/* Hidden Input: Standard File Picker (Works on Laptop & PC) */}
            <input
              ref={fileUploadInputRef}
              type="file"
              accept="image/*"
              onChange={handleInputChange}
              className="hidden"
              style={{ display: "none" }}
            />
          </div>

          {/* Action Row: When an image is ready */}
          {previewUrl && (
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleReset}
                className="flex-1 py-3 px-4 rounded-2xl bg-slate-900 hover:bg-slate-800 font-bold text-xs sm:text-sm text-slate-300 border border-slate-800 flex items-center justify-center gap-2 transition-all"
              >
                <RefreshCw className="w-4 h-4" /> Retake / Change
              </button>

              <button
                type="button"
                onClick={handleScan}
                disabled={!selectedFile || loading}
                className={`flex-1 py-3 px-4 rounded-2xl font-bold text-xs sm:text-sm text-white flex items-center justify-center gap-2 shadow-lg transition-all ${
                  !selectedFile || loading
                    ? "bg-blue-600/50 cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-blue-500/25 hover:scale-[1.02]"
                }`}
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" /> Analyzing Sign...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-300" /> Run Sign AI
                  </>
                )}
              </button>
            </div>
          )}

          {/* Compact Switch Bar below */}
          {!isCameraActive && (
            <div className="flex items-center justify-center gap-2 pt-1 text-xs text-slate-400">
              <button
                type="button"
                onClick={() => startCamera()}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
              >
                <Laptop className="w-3.5 h-3.5 text-blue-400" /> Laptop Webcam
              </button>
              <span className="text-slate-600">•</span>
              <button
                type="button"
                onClick={() => fileUploadInputRef.current?.click()}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
              >
                <Upload className="w-3.5 h-3.5 text-indigo-400" /> Upload File
              </button>
            </div>
          )}

          {/* Detection Results & Sign Meaning Card */}
          {result && (
            <div className="p-4 sm:p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl flex flex-col gap-4 animate-fade-in">
              {/* Header: Parking Rule & Status */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-semibold text-slate-400">
                  AI Sign Intelligence
                </span>
                <span
                  className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider ${
                    result.rule_type === "NO_PARKING"
                      ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                      : result.rule_type === "PAID"
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      : result.rule_type === "UNKNOWN"
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                  }`}
                >
                  {result.rule_type === "NO_PARKING"
                    ? "⛔ NO PARKING (पार्किंग मना है)"
                    : result.rule_type === "PAID"
                    ? "💰 PAID PARKING (पे एंड पार्क)"
                    : result.rule_type === "UNKNOWN"
                    ? "❓ SIGN NOT RECOGNIZED (साइन नहीं पहचाना)"
                    : "✅ PARKING PERMITTED (पार्क कर सकते हैं)"}
                </span>
              </div>

              {/* Primary Sign Title & Category */}
              <div className="flex items-start gap-3">
                {result.rule_type === "NO_PARKING" ? (
                  <div className="p-2.5 rounded-2xl bg-rose-500/20 text-rose-400 shrink-0 mt-0.5">
                    <AlertOctagon className="w-7 h-7" />
                  </div>
                ) : result.rule_type === "UNKNOWN" ? (
                  <div className="p-2.5 rounded-2xl bg-amber-500/20 text-amber-400 shrink-0 mt-0.5">
                    <HelpCircle className="w-7 h-7" />
                  </div>
                ) : (
                  <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-400 shrink-0 mt-0.5">
                    <CheckCircle className="w-7 h-7" />
                  </div>
                )}
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-extrabold text-lg text-white">
                      {result.sign_name || result.detected_signs?.[0]?.replace(/_/g, " ") || "Traffic Sign"}
                    </h3>
                    {result.sign_category && (
                      <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-blue-950/80 border border-blue-800/60 text-blue-300 uppercase">
                        {result.sign_category}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-300 mt-1">
                    {result.rule_description}
                  </p>
                </div>
              </div>

              {/* Educational Meaning & Action Grid */}
              <div className="grid grid-cols-1 gap-2.5 pt-1">
                {/* 1. Easy Sign Meaning */}
                {result.sign_meaning && (
                  <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 flex items-start gap-3">
                    <BookOpen className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <span className="text-[11px] font-extrabold text-blue-400 uppercase tracking-wider block">
                        💡 In Simple Words / आसान भाषा में
                      </span>
                      <p className="text-xs text-slate-100 mt-1 leading-relaxed font-medium">
                        {result.sign_meaning}
                      </p>
                    </div>
                  </div>
                )}

                {/* 1.5. Common Misconception / Wrong Meaning */}
                {result.wrong_meaning && (
                  <div className="p-3.5 rounded-xl bg-rose-950/25 border border-rose-900/40 flex items-start gap-3">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <span className="text-[11px] font-extrabold text-rose-400 uppercase tracking-wider block">
                        ❌ Common Mistake / लोग क्या गलत समझते हैं
                      </span>
                      <p className="text-xs text-rose-200 mt-1 leading-relaxed">
                        {result.wrong_meaning}
                      </p>
                    </div>
                  </div>
                )}

                {/* 2. Driver Action Required */}
                {result.driver_action && (
                  <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 flex items-start gap-3">
                    <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <span className="text-[11px] font-extrabold text-amber-400 uppercase tracking-wider block">
                        🚗 What You Should Do / आपको क्या करना है
                      </span>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                        {result.driver_action}
                      </p>
                    </div>
                  </div>
                )}

                {/* 3. Parking Impact & Penalties */}
                {(result.parking_impact || result.penalty_info) && (
                  <div className={`p-3.5 rounded-xl border flex items-start gap-3 ${
                    result.rule_type === "NO_PARKING"
                      ? "bg-rose-950/30 border-rose-900/50 text-rose-200"
                      : result.rule_type === "UNKNOWN"
                      ? "bg-amber-950/20 border-amber-900/40 text-amber-200"
                      : "bg-slate-950/90 border-slate-800 text-slate-300"
                  }`}>
                    <ShieldAlert className={`w-4 h-4 shrink-0 mt-0.5 ${
                      result.rule_type === "NO_PARKING"
                        ? "text-rose-400"
                        : result.rule_type === "UNKNOWN"
                        ? "text-amber-400"
                        : "text-emerald-400"
                    }`} />
                    <div className="flex-1">
                      <span className="text-[11px] font-extrabold uppercase tracking-wider block">
                        🅿️ Can I Park Here? / क्या यहाँ पार्क कर सकते हैं?
                      </span>
                      <p className="text-xs mt-1 leading-relaxed font-medium">
                        {result.parking_impact}
                      </p>
                      {result.penalty_info && (
                        <p className="text-[11px] text-rose-300 font-bold mt-1.5 flex items-center gap-1.5">
                          <span>💸 Challan / Fine:</span> {result.penalty_info}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* All Detected Signs Breakdown (if multiple signs in image) */}
              {result.all_details && result.all_details.length > 1 && (
                <div className="mt-1 pt-3 border-t border-slate-800">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                    All Detected Signs in Photo ({result.all_details.length}):
                  </span>
                  <div className="flex flex-col gap-2">
                    {result.all_details.map((detail, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs flex items-center justify-between"
                      >
                        <div>
                          <span className="font-bold text-white">{detail.name}</span>
                          <span className="text-[10px] text-slate-400 block">{detail.category}</span>
                        </div>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          detail.rule_type === "NO_PARKING"
                            ? "bg-rose-500/20 text-rose-300"
                            : "bg-emerald-500/20 text-emerald-300"
                        }`}>
                          {detail.rule_type}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Smart Feedback Loop indicator */}
              {result.saved_to_db && (
                <div className="text-[11px] text-emerald-400 bg-emerald-950/30 border border-emerald-800/40 rounded-xl p-2.5 flex items-center gap-2">
                  <Check className="w-4 h-4 shrink-0 text-emerald-400" />
                  <span>
                    <strong>Smart PostGIS Sync:</strong> Verified parking rule saved into database at your GPS coordinates!
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
