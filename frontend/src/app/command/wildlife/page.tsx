"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { WildlifeObservation } from "@/types/api";

export default function WildlifePage() {
  const [observations, setObservations] = useState<WildlifeObservation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<{ items: WildlifeObservation[] }>("/wildlife/observations", { limit: 50 })
      .then((d) => setObservations(d.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Wildlife Observations</h1>
        <span className="text-sm text-yellow-400 bg-yellow-900/30 px-2 py-1 rounded">
          Species unverified
        </span>
</div>
      <p className="text-gray-400">All species shown as "unknown" unless verified by classifier.</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-forest-700">
              <th className="p-2">Time</th>
              <th className="p-2">Camera</th>
              <th className="p-2">Species</th>
              <th className="p-2">Count</th>
              <th className="p-2">Location</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forest-700">
            {observations.map((obs) => (
              <tr key={obs.id} className="hover:bg-forest-800/50">
                <td className="p-2 text-gray-300">{new Date(obs.first_seen).toLocaleString()}</td>
                <td className="p-2 text-gray-400">{obs.camera_id.slice(0, 8)}…</td>
                <td className="p-2 text-gray-100">{obs.species}</td>
                <td className="p-2 text-gray-300">{obs.count_estimate}</td>
                <td className="p-2 text-gray-400">
                  {obs.location.coordinates[1].toFixed(4)}, {obs.location.coordinates[0].toFixed(4)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {observations.length === 0 && (
        <div className="text-center py-12 text-gray-500">No wildlife observations yet</div>
      )}
    </div>
  );
}