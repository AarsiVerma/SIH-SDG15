"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { FireEvent } from "@/types/api";

export default function FirePage() {
  const [events, setEvents] = useState<FireEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<{ items: FireEvent[] }>("/fire/events", { limit: 50 })
      .then((d) => setEvents(d.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Fire & Smoke Events</h1>
      <p className="text-gray-400">
        ⚠ No fire spread model in MVP. Severity is heuristic based on confidence only.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-forest-700">
              <th className="p-2">Time</th>
              <th className="p-2">Type</th>
              <th className="p-2">Severity</th>
              <th className="p-2">Location</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forest-700">
            {events.map((e) => (
              <tr key={e.id} className="hover:bg-forest-800/50">
                <td className="p-2 text-gray-300">{new Date(e.created_at).toLocaleString()}</td>
                <td className="p-2 capitalize text-gray-300">{e.event_type.replace(/_/g, " ")}</td>
                <td className="p-2">
                  <span
                    className={`px-2 py-0.5 rounded text-xs ${
                      e.severity === "critical" ? "bg-red-900/50 text-red-300" :
                      e.severity === "high" ? "bg-orange-900/50 text-orange-300" :
                      e.severity === "medium" ? "bg-yellow-900/50 text-yellow-300" :
                      "bg-green-900/50 text-green-300"
                    }`}
                  >
                    {e.severity}
                  </span>
                </td>
                <td className="p-2 text-gray-400 text-sm">
                  {e.location.coordinates[1].toFixed(4)}, {e.location.coordinates[0].toFixed(4)}
                </td>
                <td className="p-2">
                  <button className="text-forest-400 hover:text-forest-300 text-sm underline">
                    View nearby
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {events.length === 0 && (
        <div className="text-center py-12 text-gray-500">No fire/smoke events</div>
      )}
    </div>
  );
}