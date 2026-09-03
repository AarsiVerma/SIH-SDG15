"use client";

import { useState } from "react";
import { CameraFeed } from "@/types/dashboard";
import { Maximize2, AlertTriangle, ChevronDown } from "lucide-react";
import Image from "next/image";

interface CameraGridProps {
  cameras: CameraFeed[];
}

export function CameraGrid({ cameras }: CameraGridProps) {
  const [selectedZone, setSelectedZone] = useState("All Zones");
  const [activeModalCamera, setActiveModalCamera] = useState<CameraFeed | null>(null);

  const filteredCameras = cameras.filter((cam) => {
    if (selectedZone !== "All Zones" && cam.zone !== selectedZone) return false;
    return true;
  });

  return (
    <div className="rounded-2xl border border-[#E2E0D8] bg-white p-6 shadow-2xs dark:border-[#262626] dark:bg-[#0a0a0a]">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-5">
        <div>
          <h3 className="font-serif text-lg font-normal text-[#181918] dark:text-white">
            Live Camera Grid
          </h3>
          <p className="text-xs text-[#6B7260] dark:text-gray-400">
            Optical & thermal surveillance feeds
          </p>
        </div>

        <div className="relative">
          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="appearance-none rounded-xl border border-[#E2E0D8] bg-[#F4F5F3] px-4 py-1.5 pr-8 text-xs font-medium text-[#181918] focus:outline-none dark:border-[#262626] dark:bg-[#111111] dark:text-white"
          >
            <option>All Zones</option>
            <option>Zone 2A</option>
            <option>Zone 3F</option>
            <option>Zone 1B</option>
            <option>Zone 6E</option>
            <option>Zone 11D</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-400" />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filteredCameras.map((cam) => {
          const isAlert = cam.status === "alert";
          return (
            <div
              key={cam.id}
              onClick={() => setActiveModalCamera(cam)}
              className={`group relative aspect-[16/10] overflow-hidden rounded-xl bg-black cursor-pointer transition-all duration-300 ${
                isAlert
                  ? "ring-2 ring-red-500/80 shadow-md"
                  : "hover:ring-1 hover:ring-[#C08A3E]/50"
              }`}
            >
              <Image
                src={cam.imageUrl}
                alt={cam.name}
                fill
                className="object-cover transition-transform duration-500 group-hover:scale-105"
                sizes="(min-width: 640px) 33vw, 100vw"
              />

              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30" />

              <div className="absolute inset-x-3 top-2.5 flex items-center justify-between z-10">
                <span className="rounded-md bg-black/60 px-2 py-0.5 text-[11px] font-medium text-white backdrop-blur-xs">
                  {cam.name}
                </span>

                <div className="flex items-center gap-1.5">
                  <span className="flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 backdrop-blur-xs">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Live
                  </span>
                  {isAlert && (
                    <span className="flex items-center gap-1 rounded-full bg-red-600 px-2 py-0.5 text-[10px] font-bold text-white">
                      <AlertTriangle className="h-3 w-3" />
                    </span>
                  )}
                </div>
              </div>

              <div className="absolute inset-x-3 bottom-2.5 flex items-end justify-between z-10">
                <div>
                  {isAlert && (
                    <p className="text-[11px] font-semibold text-red-400">
                      {cam.alertMessage}
                    </p>
                  )}
                </div>

                <button className="rounded-lg bg-black/60 p-1.5 text-white opacity-0 transition-opacity group-hover:opacity-100 backdrop-blur-xs">
                  <Maximize2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {activeModalCamera && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
          onClick={() => setActiveModalCamera(null)}
        >
          <div
            className="relative w-full max-w-4xl overflow-hidden rounded-2xl bg-[#0B100C] border border-[#233026] p-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-3 text-white">
              <div>
                <h3 className="font-serif text-lg font-normal">{activeModalCamera.name}</h3>
                <p className="text-xs text-[#8A968C]">{activeModalCamera.location} &bull; Stream HD 1080p</p>
              </div>
              <button
                onClick={() => setActiveModalCamera(null)}
                className="rounded-lg bg-white/10 px-3 py-1 text-xs font-semibold hover:bg-white/20"
              >
                Close ✕
              </button>
            </div>

            <div className="relative aspect-video w-full overflow-hidden rounded-xl bg-black">
              <Image
                src={activeModalCamera.imageUrl}
                alt={activeModalCamera.name}
                fill
                className="object-cover"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
