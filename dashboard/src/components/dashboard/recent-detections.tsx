"use client";

import Image from "next/image";

export function RecentDetections() {
  const DETECTIONS = [
    {
      id: "d1",
      title: "Tiger Detected",
      location: "Zone 3F - Ridge Trail",
      time: "10:24 AM",
      priority: "High",
      imageUrl: "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=400&q=80&auto=format&fit=crop",
    },
    {
      id: "d2",
      title: "Human Intrusion",
      location: "Zone 6E - Boundary",
      time: "10:18 AM",
      priority: "High",
      imageUrl: "https://images.unsplash.com/photo-1516214104703-d870798883c5?w=400&q=80&auto=format&fit=crop",
    },
    {
      id: "d3",
      title: "Elephant Herd",
      location: "Zone 1B - Salt Lick",
      time: "10:10 AM",
      priority: "Low",
      imageUrl: "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=400&q=80&auto=format&fit=crop",
    },
    {
      id: "d4",
      title: "Leopard Detected",
      location: "Zone 7C - Grassland",
      time: "09:55 AM",
      priority: "Medium",
      imageUrl: "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=400&q=80&auto=format&fit=crop",
    },
  ];

  return (
    <div className="flex h-full flex-col rounded-2xl border border-[#E2E0D8] bg-white p-6 shadow-2xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-serif text-lg font-normal text-[#181918]">
            Recent Sightings
          </h3>
          <p className="text-xs text-[#6B7260]">
            Verified timeline feeds
          </p>
        </div>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {DETECTIONS.map((det) => {
          const isHigh = det.priority === "High";

          return (
            <div
              key={det.id}
              className="flex items-center justify-between rounded-xl border border-[#E2E0D8] bg-[#F8F8F6] p-2.5 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-lg border border-[#E2E0D8]">
                  <Image
                    src={det.imageUrl}
                    alt={det.title}
                    fill
                    className="object-cover"
                  />
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-[#181918]">
                    {det.title}
                  </h4>
                  <p className="text-[11px] text-[#6B7260]">
                    {det.location}
                  </p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-[10px] text-gray-400">{det.time}</p>
                <span
                  className={`inline-block text-[10px] font-medium ${
                    isHigh ? "text-red-500" : "text-[#C08A3E]"
                  }`}
                >
                  {det.priority}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
