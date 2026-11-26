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
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const markersRef = useRef<{ [key: number]: L.Marker }>({});
  const selectedSpotRef = useRef<ParkingSpot | null>(selectedSpot);
  const entriesRef = useRef<Array<{ spot: ParkingSpot; marker: L.Marker; priority: number; lastSelected: boolean }>>([]);

  selectedSpotRef.current = selectedSpot;

  const getPillStyle = (spot: ParkingSpot) => {
    const ruleType = (spot.rule_type || "ALLOWED").toUpperCase();
    const price = Number(spot.price_per_hour) || 0;
    if (ruleType === "NO_PARKING") {
      return { bgColor: "#E11D48", label: "NO PARK" };
    }
    if (price > 0) {
      return { bgColor: "#1C4178", label: `₹${price}/hr` };
    }
    if (spot.is_paid) {
      return { bgColor: "#1C4178", label: "PAID" };
    }
    return { bgColor: "#059669", label: "FREE" };
  };

  // Clean shadowless price pill icon (prevents dark stacking halos)
  const createCustomIcon = (spot: ParkingSpot, isSelected: boolean) => {
    const { bgColor, label } = getPillStyle(spot);
    const ringStyle = isSelected
      ? "box-shadow: 0 0 0 2px #FFCA20, 0 2px 6px rgba(15,23,42,0.22); transform: scale(1.12);"
      : "box-shadow: 0 1px 2px rgba(15,23,42,0.16);";

    const html = `
      <div style="
        position: relative;
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        width: max-content;
        transform: translate(-50%, -100%);
        cursor: pointer;
        user-select: none;
      ">
        <div style="
          background-color: ${bgColor};
          color: #ffffff;
          padding: 4px 10px;
          border-radius: 9999px;
          border: 1.5px solid #ffffff;
          font-weight: 800;
          font-size: 11px;
          line-height: 1.15;
          white-space: nowrap;
          ${ringStyle}
        ">${label}</div>
        <div style="
          width: 0;
          height: 0;
          border-left: 4px solid transparent;
          border-right: 4px solid transparent;
          border-top: 5px solid ${bgColor};
          margin-top: -1px;
        "></div>
      </div>
    `;

    return L.divIcon({
      html,
      className: "custom-park-pin",
      iconSize: [0, 0],
      iconAnchor: [0, 0],
      popupAnchor: [0, -28],
    });
  };

  const updateVisibleMarkers = () => {
    const map = mapInstanceRef.current;
    const layerGroup = markersLayerRef.current;
    if (!map || !layerGroup) return;

    const zoom = map.getZoom();
    const size = map.getSize();
    const halfW = zoom >= 14 ? 32 : 38;
    const height = zoom >= 14 ? 28 : 34;
    const currentSelectedId = selectedSpotRef.current?.id ?? null;
    const placedBoxes: Array<{ left: number; right: number; top: number; bottom: number }> = [];

    const ordered = [...entriesRef.current].sort((a, b) => {
      const aSel = a.spot.id === currentSelectedId ? 1 : 0;
      const bSel = b.spot.id === currentSelectedId ? 1 : 0;
      if (aSel !== bSel) return bSel - aSel;
      return b.priority - a.priority;
    });

    ordered.forEach((entry) => {
      const isSel = entry.spot.id === currentSelectedId;
      const pt = map.latLngToContainerPoint([entry.spot.latitude, entry.spot.longitude]);
      const inView = isSel || (pt.x >= -80 && pt.y >= -80 && pt.x <= size.x + 80 && pt.y <= size.y + 80);

      let shouldShow = false;
      if (inView) {
        const box = { left: pt.x - halfW, right: pt.x + halfW, top: pt.y - height, bottom: pt.y + 4 };
        const overlaps = !isSel && placedBoxes.some(
          (b) => box.left < b.right && box.right > b.left && box.top < b.bottom && box.bottom > b.top
        );
        if (!overlaps) {
          placedBoxes.push(box);
          shouldShow = true;
        }
      }

      if (shouldShow) {
        if (entry.lastSelected !== isSel) {
          entry.marker.setIcon(createCustomIcon(entry.spot, isSel));
          entry.lastSelected = isSel;
        }
        entry.marker.setZIndexOffset(isSel ? 1000 : entry.priority >= 1000 ? 500 : 0);
        if (!layerGroup.hasLayer(entry.marker)) {
          layerGroup.addLayer(entry.marker);
        }
      } else if (layerGroup.hasLayer(entry.marker)) {
        layerGroup.removeLayer(entry.marker);
      }
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

      markersLayerRef.current = L.layerGroup().addTo(map);
      map.on("zoomend moveend", updateVisibleMarkers);
      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;
    const layerGroup = markersLayerRef.current;
    if (layerGroup) layerGroup.clearLayers();
    markersRef.current = {};
    entriesRef.current = [];

    if (spots.length === 0) return;

    const bounds = L.latLngBounds([]);

    spots.forEach((spot) => {
      const isSelected = selectedSpotRef.current?.id === spot.id;
      const marker = L.marker([spot.latitude, spot.longitude], {
        icon: createCustomIcon(spot, isSelected),
        title: spot.name,
      });

      const priceText =
        spot.rule_type === "NO_PARKING"
          ? "No Parking Zone"
          : spot.price_per_hour > 0
          ? `Paid: ₹${spot.price_per_hour}/hr`
          : spot.is_paid
          ? "Paid Parking"
          : "Free Parking";

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
            ${priceText}
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

      const price = Number(spot.price_per_hour) || 0;
      const isNoParking = (spot.rule_type || "").toUpperCase() === "NO_PARKING";
      const isUnnamedOsm =
        /^Unnamed Parking/i.test(spot.name || "") || /^Chandigarh Parking \(osm_/i.test(spot.name || "");
      const priority =
        !isNoParking && price > 0
          ? 1000 + price
          : !isNoParking && !isUnnamedOsm
          ? 500 + (spot.is_paid ? 40 : 0) + (spot.available_car_slots > 0 ? 20 : 0)
          : isNoParking
          ? 300
          : (spot.available_car_slots + spot.available_bike_slots > 0 ? 100 : 10) + (spot.is_paid ? 5 : 0);

      markersRef.current[spot.id] = marker;
      entriesRef.current.push({ spot, marker, priority, lastSelected: isSelected });
      bounds.extend([spot.latitude, spot.longitude]);
    });

    // Fit bounds if we have spots and no single spot is focused
    if (!selectedSpotRef.current && spots.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
    }
    updateVisibleMarkers();
  }, [spots]);

  // Center on selected spot
  useEffect(() => {
    updateVisibleMarkers();
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
