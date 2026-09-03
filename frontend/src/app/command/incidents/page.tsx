"use client";

import { useState } from "react";
import { api } from "@/lib/api/client";
import { Incident, IncidentStatus } from "@/types/api";
import IncidentDetail from "@/components/incidents/IncidentDetail";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selected, setSelected] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: "",
    level: "",
    search: "",
  });

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { limit: "50" };
      if (filters.status) params.status = filters.status;
      if (filters.level) params.risk_level = filters.level;
      if (filters.search) params.search = filters.search;

      const data = await api.get<{ items: Incident[] }>("/incidents", params);
      setIncidents(data.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full gap-4">
      {/* Sidebar - List */}
      <div className="w-96 bg-forest-800 rounded-xl border border-forest-700 flex flex-col">
        <div className="p-4 border-b border-forest-700">
          <h2 className="font-semibold text-lg mb-3">Incidents</h2>
          <div className="space-y-2">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full bg-forest-900 border border-forest-700 rounded px-2 py-1 text-sm"
            >
              <option value="">All Status</option>
              <option value="NEW">New</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="DISPATCHED">Dispatched</option>
              <option value="RESOLVED">Resolved</option>
              <option value="CLOSED">Closed</option>
            </select>
            <select
              value={filters.level}
              onChange={(e) => setFilters({ ...filters, level: e.target.value })}
              className="w-full bg-forest-900 border border-forest-700 rounded px-2 py-1 text-sm"
            >
              <option value="">All Levels</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
            <input
              type="text"
              placeholder="Search public_id..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full bg-forest-900 border border-forest-700 rounded px-2 py-1 text-sm"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-400">Loading…</div>
          ) : (
            <ul className="divide-y divide-forest-700">
              {incidents.map((inc) => (
                <li key={inc.id}>
                  <button
                    onClick={() => setSelected(inc)}
                    className={`w-full text-left p-3 hover:bg-forest-700 transition ${
                      selected?.id === inc.id ? "bg-forest-700" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-sm text-forest-300">{inc.public_id}</span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${
                          inc.risk_level === "CRITICAL"
                            ? "bg-red-900/50 text-red-300"
                            : inc.risk_level === "HIGH"
                            ? "bg-orange-900/50 text-orange-300"
                            : inc.risk_level === "MEDIUM"
                            ? "bg-yellow-900/50 text-yellow-300"
                            : "bg-green-900/50 text-green-300"
                        }`}
                      >
                        {inc.risk_level}
                      </span>
                    </div>
                    <div className="text-sm text-gray-300">{inc.title}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(inc.created_at).toLocaleString()}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Detail Panel */}
      <div className="flex-1">
        {selected ? (
          <IncidentDetail incident={selected} onClose={() => setSelected(null)} />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500">
            Select an incident to view details
          </div>
        )}
      </div>
    </div>
  );
}