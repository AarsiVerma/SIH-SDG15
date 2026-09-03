"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";

interface CameraHealth {
  id: string;
  camera_id: string;
  state: "online" | "offline" | "degraded" | "unknown";
  last_heartbeat: string | null;
  last_frame_at: string | null;
  last_detection_at: string | null;
  notes: string | null;
}

export default function HealthPage() {
  const [health, setHealth] = useState<CameraHealth[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<CameraHealth[]>("/cameras/health", { limit: 100 })
      .then(setHealth)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const getStateColor = (state: string) => {
    switch (state) {
      case "online": return "bg-green-900/50 text-green-300";
      case "offline": return "bg-red-900/50 text-red-300";
      case "degraded": return "bg-yellow-900/50 text-yellow-300";
      default: return "bg-gray-700 text-gray-400";
    }
  };

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Camera Health</h1>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-forest-700">
              <th className="p-2">Camera</th>
              <th className="p-2">State</th>
              <th className="p-2">Last Frame</th>
              <th className="p-2">Last Detection</th>
              <th className="p-2">Reason</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forest-700">
            {health.map((h) => (
              <tr key={h.id} className="hover:bg-forest-800/50">
                <td className="p-2 font-mono text-gray-300">{h.camera_id.slice(0, 8)}…</td>
                <td className="p-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${getStateColor(h.state)}`}>
                    {h.state}
                  </span>
                </td>
                <td className="p-2 text-gray-300">
                  {h.last_frame_at ? new Date(h.last_frame_at).toLocaleTimeString() : "Never"}
                </td>
                <td className="p-2 text-gray-300">
                  {h.last_detection_at ? new Date(h.last_detection_at).toLocaleTimeString() : "Never"}
                </td>
                <td className="p-2 text-gray-400 text-sm">{h.notes || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {health.length === 0 && (
        <div className="text-center py-12 text-gray-500">No camera health data</div>
      )}
    </div>
  );
}