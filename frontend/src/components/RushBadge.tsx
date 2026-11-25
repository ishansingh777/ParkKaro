"use client";

import React, { useEffect, useState } from "react";
import { predictRush } from "@/lib/api";
import { RushPrediction } from "@/types";
import { Sparkles, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";

interface RushBadgeProps {
  spotId: number;
  initialHour?: number;
}

export default function RushBadge({ spotId, initialHour }: RushBadgeProps) {
  const [prediction, setPrediction] = useState<RushPrediction | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedHour, setSelectedHour] = useState<number>(
    initialHour !== undefined ? initialHour : new Date().getHours()
  );

  useEffect(() => {
    let isMounted = true;
    const dayOfWeek = new Date().getDay(); // 0 is Sunday, 6 is Saturday

    setLoading(true);
    predictRush(spotId, selectedHour, dayOfWeek)
      .then((data) => {
        if (isMounted) setPrediction(data);
      })
      .catch((err) => {
        console.error("Rush prediction error:", err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [spotId, selectedHour]);

  const formatHour = (h: number) => {
    const period = h >= 12 ? "PM" : "AM";
    const hour12 = h % 12 === 0 ? 12 : h % 12;
    return `${hour12} ${period}`;
  };

  if (loading) {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 text-xs border border-indigo-100 animate-pulse">
        <Sparkles className="w-3.5 h-3.5 text-indigo-500 animate-spin" />
        <span>Predicting AI rush...</span>
      </div>
    );
  }

  if (!prediction) {
    return null;
  }

  const isHard = prediction.status === "Hard to find parking";
  const isModerate = prediction.status === "Moderate rush";

  return (
    <div className="flex flex-col gap-1.5 p-2.5 rounded-xl bg-gradient-to-r from-slate-50 to-indigo-50/50 border border-indigo-100">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold text-slate-700 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
          AI Rush Forecast
        </span>
        <select
          value={selectedHour}
          onChange={(e) => setSelectedHour(Number(e.target.value))}
          className="bg-white border border-slate-200 text-slate-700 rounded-md text-[11px] px-1.5 py-0.5 font-medium"
        >
          {Array.from({ length: 24 }).map((_, i) => (
            <option key={i} value={i}>
              {formatHour(i)}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          {isHard ? (
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          ) : isModerate ? (
            <TrendingUp className="w-4 h-4 text-amber-500" />
          ) : (
            <CheckCircle className="w-4 h-4 text-emerald-500" />
          )}
          <span
            className={`text-xs font-bold ${
              isHard
                ? "text-rose-600"
                : isModerate
                ? "text-amber-600"
                : "text-emerald-600"
            }`}
          >
            {formatHour(selectedHour)}: {prediction.chance_of_full} full
          </span>
        </div>
        <span className="text-[11px] text-slate-500 font-medium truncate">
          {prediction.status}
        </span>
      </div>
    </div>
  );
}
