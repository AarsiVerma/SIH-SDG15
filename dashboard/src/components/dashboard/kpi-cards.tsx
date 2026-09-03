"use client";

import { Video, ShieldAlert, Footprints, Truck, ShieldCheck } from "lucide-react";

export function KPICards() {
  const KPIS = [
    {
      title: "Total Cameras",
      value: "142",
      subtext: "Out of 158",
      icon: Video,
    },
    {
      title: "Active Alerts",
      value: "06",
      subtext: "High Priority",
      icon: ShieldAlert,
      isAlert: true,
    },
    {
      title: "Wildlife Sightings",
      value: "23",
      subtext: "Logged Today",
      icon: Footprints,
    },
    {
      title: "Patrol Units",
      value: "08",
      subtext: "Active in Field",
      icon: Truck,
    },
    {
      title: "System Status",
      value: "99.6%",
      subtext: "Operational Uptime",
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {KPIS.map((kpi) => {
        const Icon = kpi.icon;
        return (
          <div
            key={kpi.title}
            className="rounded-2xl border border-[#E2E0D8] bg-white p-5 shadow-2xs transition-all hover:border-gray-300"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[#6B7260]">
                {kpi.title}
              </span>
              <Icon
                className={`h-4 w-4 ${
                  kpi.isAlert ? "text-red-500" : "text-[#C08A3E]"
                }`}
              />
            </div>

            <p className="mt-3 font-serif text-3xl font-normal tracking-tight text-[#181918]">
              {kpi.value}
            </p>

            <p className="mt-1 text-[11px] text-[#6B7260]">
              {kpi.subtext}
            </p>
          </div>
        );
      })}
    </div>
  );
}
