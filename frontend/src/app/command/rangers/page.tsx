"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Ranger } from "@/types/api";

export default function RangersPage() {
  const [rangers, setRangers] = useState<Ranger[]>([]);
  const [loading, setLoading] = useState(true);
  const [sosLoading, setSosLoading] = useState<string | null>(null);

  useEffect(() => {
    api.get<{ items: Ranger[] }>("/rangers", { limit: 50 })
      .then((d) => setRangers(d.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSos = async (rangerId: string) => {
    if (!confirm("Trigger SOS for this ranger? This creates a CRITICAL incident.")) return;
    setSosLoading(rangerId);
    try {
      await api.post(`/sos/rangers/${rangerId}/sos`, {});
      alert("SOS triggered successfully. CRITICAL incident created.");
    } catch (e) {
      console.error(e);
      alert("Failed to trigger SOS");
    } finally {
      setSosLoading(null);
    }
  };

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Rangers</h1>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-forest-700">
              <th className="p-2">Badge</th>
              <th className="p-2">Name</th>
              <th className="p-2">Status</th>
              <th className="p-2">Simulated</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forest-700">
            {rangers.map((r) => (
              <tr key={r.id} className="hover:bg-forest-800/50">
                <td className="p-2 font-mono text-gray-300">{r.badge_code}</td>
                <td className="p-2 text-gray-100">{r.name}</td>
                <td className="p-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    r.active ? "bg-green-900/50 text-green-300" : "bg-gray-700 text-gray-400"
                  }`}>
                    {r.active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="p-2 text-center">
                  {r.is_simulated ? (
                    <span className="px-2 py-0.5 rounded text-xs bg-blue-900/50 text-blue-300">Sim</span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-400">Real</span>
                  )}
                </td>
                <td className="p-2">
                  <button
                    onClick={() => handleSos(r.id)}
                    disabled={sosLoading === r.id}
                    className="w-full bg-red-900/50 hover:bg-red-900 text-red-300 py-1 rounded text-sm transition disabled:opacity-50"
                  >
                    {sosLoading === r.id ? "Triggering…" : "🆘 SOS"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rangers.length === 0 && (
        <div className="text-center py-12 text-gray-500">No rangers</div>
      )}
    </div>
  );
}