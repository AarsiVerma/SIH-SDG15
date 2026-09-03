"use client";

import { useState } from "react";
import { Incident, IncidentStatus } from "@/types/api";
import { api } from "@/lib/api/client";
import VerificationBanner from "@/components/copy/VerificationBanner";

interface IncidentDetailProps {
  incident: Incident;
  onClose: () => void;
}

export default function IncidentDetail({ incident, onClose }: IncidentDetailProps) {
  const [detail, setDetail] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [transitioning, setTransitioning] = useState(false);

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const data = await api.get<Incident>(`/incidents/${incident.id}`);
      setDetail(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleTransition = async (toStatus: IncidentStatus) => {
    setTransitioning(true);
    try {
      await api.post(`/incidents/${incident.id}/transition`, { to_status: toStatus });
      fetchDetail();
    } catch (e) {
      console.error(e);
      alert("Transition failed");
    } finally {
      setTransitioning(false);
    }
  };

  const statusOrder: IncidentStatus[] = [
    "NEW",
    "ACKNOWLEDGED",
    "INVESTIGATING",
    "DISPATCHED",
    "RESOLVED",
    "CLOSED",
  ];

  const currentIndex = statusOrder.indexOf(incident.status);
  const nextStatus = currentIndex >= 0 && currentIndex < statusOrder.length - 1
    ? statusOrder[currentIndex + 1]
    : null;

  const header = (
    <div className="flex items-center justify-between p-4 border-b border-forest-700">
      <div>
        <div className="flex items-center gap-3">
          <button onClick={onClose} className="text-gray-400 hover:text-gray-100">←</button>
          <span className="font-mono text-sm text-forest-300">{incident.public_id}</span>
        </div>
        <h2 className="text-lg font-semibold text-gray-100 mt-1">{incident.title}</h2>
      </div>
      <span
        className={`px-3 py-1 rounded text-sm ${
          incident.risk_level === "CRITICAL"
            ? "bg-red-900/50 text-red-300"
            : incident.risk_level === "HIGH"
            ? "bg-orange-900/50 text-orange-300"
            : incident.risk_level === "MEDIUM"
            ? "bg-yellow-900/50 text-yellow-300"
            : "bg-green-900/50 text-green-300"
        }`}
      >
        {incident.risk_level}
      </span>
    </div>
  );

  return (
    <div className="flex flex-col h-full bg-forest-800 rounded-xl border border-forest-700 overflow-hidden">
      {header}
      {loading ? (
        <div className="flex-1 flex items-center justify-center">Loading…</div>
      ) : !detail ? (
        <div className="flex-1 flex items-center justify-center">No detail available</div>
      ) : (
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Verification Banner */}
          {(["HIGH", "CRITICAL"].includes(incident.risk_level || "")) && (
            <VerificationBanner level={incident.risk_level! as "CRITICAL" | "HIGH"} />
          )}

          {/* Risk Breakdown */}
          <div className="bg-forest-900/50 rounded-lg p-4 border border-forest-700">
            <h3 className="font-semibold mb-3">Risk Assessment</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-400">Score</p>
                <p className="text-2xl font-bold text-gray-100">{detail!.risk_score ?? 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Level</p>
                <p className="text-2xl font-bold capitalize">{detail!.risk_level?.toLowerCase()}</p>
              </div>
            </div>
            {detail!.factors?.length && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-300">Contributing Factors</p>
                {detail!.factors.map((f, i) => (
                  <div key={i} className="text-sm flex justify-between text-gray-300">
                    <span>{f.reason}</span>
                    <span className={f.delta >= 0 ? "text-red-400" : "text-green-400"}>
                      {f.delta >= 0 ? "+" : ""}{f.delta}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Related Events */}
          {detail!.events?.length && (
            <div>
              <h3 className="font-semibold mb-2">Related Events</h3>
              <div className="space-y-1">
                {detail!.events.map((e) => (
                  <div key={e.id} className="bg-forest-900/50 rounded p-3 border border-forest-700 text-sm">
                    <div className="flex justify-between">
                      <span className="capitalize">{e.event_type.replace(/_/g, " ")}</span>
                      <span className="text-gray-400">{new Date(e.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Evidence */}
          {detail!.evidence?.length && (
            <div>
              <h3 className="font-semibold mb-2">Evidence</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {detail!.evidence.map((ev) => (
                  <div key={ev.id} className="relative aspect-square bg-forest-900 rounded border border-forest-700 overflow-hidden">
                    <img
                      src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/evidence/${ev.id}/file`}
                      alt="Evidence"
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Status Transition */}
          <div className="border-t border-forest-700 pt-4">
            <h3 className="font-semibold mb-3">Status: {incident.status}</h3>
            {nextStatus && (
              <button
                onClick={() => handleTransition(nextStatus)}
                disabled={transitioning}
                className="w-full bg-forest-600 hover:bg-forest-500 text-white py-2 rounded disabled:opacity-50"
              >
                {transitioning ? "Transitioning…" : `Transition to ${nextStatus}`}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}