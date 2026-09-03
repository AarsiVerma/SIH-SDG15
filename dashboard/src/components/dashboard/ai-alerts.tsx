"use client";

import { useState } from "react";
import { AIAlert } from "@/types/dashboard";
import Image from "next/image";

interface AIAlertsProps {
  alerts: AIAlert[];
}

export function AIAlerts({ alerts }: AIAlertsProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const categories = ["All", "Wildlife", "Intrusion", "Fire", "Vehicle"];

  const filteredAlerts = alerts.filter(
    (alert) => selectedCategory === "All" || alert.category === selectedCategory
  );

  return (
    <div className="flex h-full flex-col rounded-2xl border border-[#E2E0D8] bg-white p-6 shadow-2xs">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-serif text-lg font-normal text-[#181918]">
            AI Alerts ({alerts.length})
          </h3>
          <p className="text-xs text-[#6B7260]">
            Automated hazard & detection logs
          </p>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-1.5 border-b border-[#E2E0D8] pb-3">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`rounded-lg px-2.5 py-1 text-xs transition-all ${
              selectedCategory === cat
                ? "bg-[#181918] text-white font-medium"
                : "text-[#6B7260] hover:bg-[#F4F5F3]"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="mt-4 flex-1 space-y-3 overflow-y-auto pr-1">
        {filteredAlerts.map((alert) => {
          const isHigh = alert.priority === "High";

          return (
            <div
              key={alert.id}
              className="flex items-center justify-between rounded-xl border border-[#E2E0D8] bg-[#F8F8F6] p-3 transition-all hover:border-gray-300"
            >
              <div className="flex items-center gap-3">
                <div className="relative h-11 w-11 shrink-0 overflow-hidden rounded-lg border border-[#E2E0D8]">
                  <Image
                    src={alert.imageUrl}
                    alt={alert.title}
                    fill
                    className="object-cover"
                  />
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-[#181918]">
                    {alert.title}
                  </h4>
                  <p className="text-[11px] text-[#6B7260]">
                    {alert.zone} &bull; {alert.location}
                  </p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-[10px] text-gray-400">{alert.time}</p>
                <span
                  className={`inline-block rounded-md px-1.5 py-0.5 text-[10px] font-semibold ${
                    isHigh
                      ? "bg-red-50 text-red-600 border border-red-200"
                      : "bg-[#C08A3E]/10 text-[#C08A3E]"
                  }`}
                >
                  {alert.priority}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
