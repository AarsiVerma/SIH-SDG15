"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { DashboardSummary } from "@/types/api";
import StatCard from "@/components/overview/StatCard";

export default function CommandOverview() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<DashboardSummary>("/dashboard/summary")
      .then(setSummary)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex h-64 items-center justify-center">Loading…</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-100">Command Centre Overview</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Open Incidents"
          value={summary?.open_incidents ?? 0}
          icon="🚨"
          color="red"
          trend={`${summary?.incidents_by_level?.CRITICAL ?? 0} critical`}
        />
        <StatCard
          label="Cameras Online"
          value={`${summary?.cameras_online ?? 0} / ${summary?.cameras_total ?? 0}`}
          icon="📹"
          color="green"
        />
        <StatCard
          label="Active Rangers"
          value={summary?.rangers_active ?? 0}
          icon="👮"
          color="blue"
        />
        <StatCard
          label="Last SOS"
          value={summary?.last_sos_at ? new Date(summary.last_sos_at).toLocaleTimeString() : "None"}
          icon="🆘"
          color="yellow"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-forest-800 rounded-xl border border-forest-700 p-5">
          <h2 className="text-lg font-semibold mb-4 text-gray-100">Incidents by Level</h2>
          <div className="space-y-2">
            {summary?.incidents_by_level &&
              Object.entries(summary.incidents_by_level).map(([level, count]) => (
                <div key={level} className="flex justify-between text-sm">
                  <span className="capitalize text-gray-300">{level.toLowerCase()}</span>
                  <span className="font-medium text-gray-100">{count}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="bg-forest-800 rounded-xl border border-forest-700 p-5">
          <h2 className="text-lg font-semibold mb-4 text-gray-100">System Status</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-300">API</span>
              <span className="text-green-400">Operational</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">WebSocket</span>
              <span className="text-green-400">Connected</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">Database</span>
              <span className="text-green-400">Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}