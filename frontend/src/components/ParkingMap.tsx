"use client";

import React, { useEffect, useRef } from "react";
import { ParkingSpot } from "../types";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

interface ParkingMapProps {
  spots: ParkingSpot[];
  selectedSpot: ParkingSpot | null;
  onSelectSpot: (spot: ParkingSpot) => void;
  onBookSpot: (spot: ParkingSpot) => void;
}

export default function ParkingMap({
  spots,
  selectedSpot,
  onSelectSpot,
  onBookSpot,
}: ParkingMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<{ [key: number]: L.Marker }>({});

  // Custom Div Icons for crisp rendering without external assets
  const createCustomIcon = (ruleType: string, isSelected: boolean) => {
    let bgColor = "#2563EB"; // Blue for PAID
    let label = "₹";
    if (ruleType === "ALLOWED") {
      bgColor = "#10B981"; // Green for ALLOWED
      label = "P";
    } else if (ruleType === "NO_PARKING") {
      bgColor = "#EF4444"; // Red for NO_PARKING
      label = "⛔";
    }

    const size = isSelected ? 42 : 34;

    const html = `
      <div style="
        background-color: ${bgColor};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        border: 2px solid #ffffff;
        cursor: pointer;
        transition: transform 0.2s ease;
      ">
        <span style="
          transform: rotate(45deg);
          color: #ffffff;
          font-weight: 800;
          font-size: ${isSelected ? 16 : 13}px;
          user-select: none;
        ">${label}</span>
      </div>
    `;

    return L.divIcon({
      html,
      className: "custom-park-pin",
      iconSize: [size, size],
      iconAnchor: [size / 2, size],
      popupAnchor: [0, -size],
    });
  };

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize map centered roughly in Central/North India (Indore / Bhopal center)
      const map = L.map(mapContainerRef.current, {
        center: [22.7196, 75.8577], // Indore default
        zoom: 6,
        zoomControl: true,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;

    // Clear old markers
    Object.values(markersRef.current).forEach((marker) => marker.remove());
    markersRef.current = {};

    if (spots.length === 0) return;

    const bounds = L.latLngBounds([]);

    spots.forEach((spot) => {
      const isSelected = selectedSpot?.id === spot.id;
      const marker = L.marker([spot.latitude, spot.longitude], {
        icon: createCustomIcon(spot.rule_type, isSelected),
        title: spot.name,
      }).addTo(map);

      // Popup Content
      const popupHtml = `
        <div style="font-family: inherit; min-width: 180px; padding: 4px;">
          <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">
            ${spot.city}
          </div>
          <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-bottom: 4px;">
            ${spot.name}
          </div>
          <div style="font-size: 12px; color: #475569; margin-bottom: 8px;">
            ${spot.is_paid ? `Paid: ₹${spot.price_per_hour}/hr` : spot.rule_type === 'ALLOWED' ? 'Free Parking' : 'No Parking Zone'}
          </div>
          <div style="font-size: 11px; color: #16a34a; font-weight: 600; margin-bottom: 8px;">
            Available: 🚗 ${spot.available_car_slots} | 🏍️ ${spot.available_bike_slots}
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);

      marker.on("click", () => {
        onSelectSpot(spot);
      });

      markersRef.current[spot.id] = marker;
      bounds.extend([spot.latitude, spot.longitude]);
    });

    // Fit bounds if we have spots and no single spot is focused
    if (!selectedSpot && spots.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
    }
  }, [spots]);

  // Center on selected spot
  useEffect(() => {
    if (selectedSpot && mapInstanceRef.current) {
      mapInstanceRef.current.flyTo(
        [selectedSpot.latitude, selectedSpot.longitude],
        15,
        { duration: 1.2 }
      );

      const targetMarker = markersRef.current[selectedSpot.id];
      if (targetMarker) {
        targetMarker.openPopup();
      }
    }
  }, [selectedSpot]);

  return (
    <div className="relative w-full h-[520px] lg:h-[680px] rounded-3xl overflow-hidden border border-slate-200 shadow-md">
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-[500] bg-white/95 backdrop-blur-md rounded-2xl p-3 shadow-lg border border-slate-200 text-xs flex flex-col gap-1.5">
        <span className="font-bold text-slate-800 text-[11px] uppercase tracking-wider mb-0.5">
          Parking Rules
        </span>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-emerald-200" />
          <span className="text-slate-600 font-medium">Free / Allowed</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-blue-600 ring-2 ring-blue-200" />
          <span className="text-slate-600 font-medium">Paid Municipal / Lot</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-rose-500 ring-2 ring-rose-200" />
          <span className="text-slate-600 font-medium">No Parking / Tow Zone</span>
        </div>
      </div>
    </div>
  );
}
