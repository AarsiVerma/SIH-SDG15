"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";

interface AnalyticsData {
  incidents_per_day: { date: string; count: number }[];
  by_type: { type: string; count: number }[];
  by_level: { level: string; count: number }[];
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState({ days: 30 });

  useEffect(() => {
    const params = { from: new Date(Date.now() - range.days * 864e5).toISOString().split("T")[0] };
    api.get<AnalyticsData>("/analytics/incidents", params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [range]);

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <select
          value={range.days}
          onChange={(e) => setRange({ days: Number(e.target.value) })}
          className="bg-forest-900 border border-forest-700 rounded px-3 py-1 text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Incidents per day */}
        <div className="bg-forest-800 rounded-xl border border-forest-700 p-5">
          <h3 className="font-semibold mb-4">Incidents per Day</h3>
          <div className="h-64 flex items-end gap-1">
            {data?.incidents_per_day?.map((d, i) => (
              <div key={i} className="flex-1 flex flex-col items-end">
                <div
                  className="bg-forest-500 rounded-t w-full transition-all"
                  style={{ height: `${Math.max(4, (d.count / (Math.max(...(data.incidents_per_day.map(x => x.count)) || 1))) * 100)}%` }}
                />
                <span className="text-xs text-gray-400 mt-1">{d.date.slice(5)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* By type */}
        <div className="bg-forest-800 rounded-xl border border-forest-700 p-5">
          <h3 className="font-semibold mb-4">By Type</h3>
          <div className="space-y-2">
            {data?.by_type?.map((d) => (
              <div key={d.type} className="flex justify-between text-sm">
                <span className="capitalize text-gray-300">{d.type.replace(/_/g, " ")}</span>
                <span className="font-medium text-gray-100">{d.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* By level */}
        <div className="bg-forest-800 rounded-xl border border-forest-700 p-5">
          <h3 className="font-semibold mb-4">By Risk Level</h3>
          <div className="space-y-2">
            {data?.by_level?.map((d) => (
              <div key={d.level} className="flex justify-between text-sm">
                <span
                  className={`capitalize ${
                    d.level === "CRITICAL" ? "text-red-300" :
                    d.level === "HIGH" ? "text-orange-300" :
                    d.level === "MEDIUM" ? "text-yellow-300" : "text-green-300"
                  }`}
                >
                  {d.level.toLowerCase()}
                </span>
                <span className="font-medium text-gray-100">{d.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {!data && <div className="text-center py-12 text-gray-500">No analytics data</div>}
    </div>
  );
}