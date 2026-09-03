"use client";

import { MAP_MARKERS } from "@/types/dashboard";
import { Plus, Minus, Video, ShieldAlert, Truck, Flag } from "lucide-react";
import Image from "next/image";

export function MapView() {
  return (
    <div className="relative flex h-full flex-col overflow-hidden rounded-2xl border border-[#233026] bg-[#0A0F0C] p-6 text-white shadow-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-serif text-lg font-normal text-[#F1EFE8]">
            Live Map View
          </h3>
          <p className="text-xs text-[#8A968C]">
            Spatial sector boundaries & asset tracking
          </p>
        </div>
      </div>

      <div className="relative min-h-[300px] flex-1 overflow-hidden rounded-xl border border-[#233026] bg-[#070C09]">
        <Image
          src="https://images.unsplash.com/photo-1524661135-423995f22d0b?w=1200&q=80&auto=format&fit=crop"
          alt="Reserve GIS Map"
          fill
          className="object-cover opacity-50 mix-blend-luminosity"
        />

        <svg className="absolute inset-0 h-full w-full stroke-emerald-500/20" fill="none">
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" strokeWidth="0.5" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />
          <path
            d="M 120 80 L 220 140 L 380 90 L 450 180 L 300 240 L 150 200 Z"
            stroke="#C08A3E"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />
        </svg>

        {MAP_MARKERS.map((marker) => {
          const isAlert = marker.type === "alert";
          const isCamera = marker.type === "camera";
          const isPatrol = marker.type === "patrol";

          return (
            <div
              key={marker.id}
              style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
              className="group absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10"
            >
              <div
                className={`flex h-6 w-6 items-center justify-center rounded-full shadow-md transition-transform hover:scale-125 ${
                  isAlert
                    ? "bg-red-600 text-white animate-pulse"
                    : isCamera
                    ? "bg-emerald-600 text-white"
                    : isPatrol
                    ? "bg-blue-600 text-white"
                    : "bg-[#C08A3E] text-white"
                }`}
              >
                {isAlert && <ShieldAlert className="h-3 w-3" />}
                {isCamera && <Video className="h-3 w-3" />}
                {isPatrol && <Truck className="h-3 w-3" />}
                {!isAlert && !isCamera && !isPatrol && <Flag className="h-3 w-3" />}
              </div>

              <div className="absolute bottom-full left-1/2 mb-1.5 hidden -translate-x-1/2 whitespace-nowrap rounded-md bg-black/90 px-2 py-1 text-[10px] text-white shadow-lg group-hover:block backdrop-blur-xs">
                {marker.label}
              </div>
            </div>
          );
        })}

        <div className="absolute left-3 top-3 flex flex-col gap-1 rounded-lg border border-white/10 bg-black/70 p-1 backdrop-blur-md">
          <button className="rounded p-1 text-white hover:bg-white/20">
            <Plus className="h-3.5 w-3.5" />
          </button>
          <button className="rounded p-1 text-white hover:bg-white/20">
            <Minus className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="absolute bottom-3 inset-x-3 flex items-center justify-between rounded-lg border border-white/10 bg-black/80 px-3 py-1.5 text-[10px] text-gray-300 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-emerald-500" /> Camera
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-red-500" /> Alert
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-blue-500" /> Patrol
            </span>
          </div>
          <span className="text-[#C08A3E] font-medium">&mdash; Sector Boundary</span>
        </div>
      </div>
    </div>
  );
}
