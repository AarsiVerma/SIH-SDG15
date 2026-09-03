"use client";

import { TreePine, CloudRain, MapPin } from "lucide-react";

export function FooterBar() {
  return (
    <footer className="mt-6 flex flex-col gap-3 rounded-2xl border border-[#E2E0D8] bg-white px-6 py-3 text-xs text-[#6B7260] shadow-2xs transition-colors dark:border-[#262626] dark:bg-[#0a0a0a] dark:text-gray-400 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-2 font-medium">
        <TreePine className="h-4 w-4 text-[#C08A3E]" />
        <span>
          AI Model Active &bull; Monitoring <strong className="text-[#181918] dark:text-white">142 active streams</strong>
        </span>
      </div>

      <div className="flex items-center gap-4 text-[11px]">
        <div className="flex items-center gap-1">
          <CloudRain className="h-3.5 w-3.5 text-blue-500" />
          <span>28°C &bull; Light Rain</span>
        </div>
        <div className="flex items-center gap-1 font-medium text-[#181918] dark:text-white">
          <MapPin className="h-3.5 w-3.5 text-emerald-500" />
          <span>Ranthambore Reserve</span>
        </div>
      </div>
    </footer>
  );
}
