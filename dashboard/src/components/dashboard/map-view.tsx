"use client";

import { useState } from "react";
import { Plus, Minus, Video, ShieldAlert, Truck, Flag } from "lucide-react";
import dynamic from "next/dynamic";
import { MapillaryViewer } from "./MapillaryViewer";

const LeafletMap = dynamic(
  () => import("./LeafletMap").then((mod) => mod.LeafletMap),
  { ssr: false, loading: () => <div className="flex h-full items-center justify-center text-gray-500">Loading map...</div> }
);

export function MapView() {
  const [selectedPosition, setSelectedPosition] = useState<{ lat: number; lng: number } | null>(null);

  const handleMarkerClick = (position: [number, number], _label: string) => {
    setSelectedPosition({ lat: position[0], lng: position[1] });
  };

  const handleCloseMapillary = () => {
    setSelectedPosition(null);
  };

  return (
    <div className="relative flex h-full flex-col overflow-hidden rounded-2xl border border-[#233026] bg-[#0A0F0C] p-6 text-white shadow-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-serif text-lg font-normal text-[#F1EFE8]">
            Live Map View
          </h3>
          <p className="text-xs text-[#8A968C]">
            Ranthambore National Park &mdash; Spatial sector boundaries & asset tracking
          </p>
        </div>
      </div>

      <div className="relative min-h-[300px] flex-1 overflow-hidden rounded-xl border border-[#233026] bg-[#070C09]">
        <LeafletMap onMarkerClick={handleMarkerClick} />

        <div className="absolute left-3 top-3 flex flex-col gap-1 rounded-lg border border-white/10 bg-black/70 p-1 backdrop-blur-md z-10">
          <button className="rounded p-1 text-white hover:bg-white/20" title="Zoom In">
            <Plus className="h-3.5 w-3.5" />
          </button>
          <button className="rounded p-1 text-white hover:bg-white/20" title="Zoom Out">
            <Minus className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="absolute bottom-3 inset-x-3 flex items-center justify-between rounded-lg border border-white/10 bg-black/80 px-3 py-1.5 text-[10px] text-gray-300 backdrop-blur-md z-10">
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

      {selectedPosition && (
        <MapillaryViewer position={selectedPosition} onClose={handleCloseMapillary} />
      )}
    </div>
  );
}