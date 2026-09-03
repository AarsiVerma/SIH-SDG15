"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Evidence } from "@/types/api";
import EvidenceDisclaimer from "@/components/copy/EvidenceDisclaimer";

export default function EvidencePage() {
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [selected, setSelected] = useState<Evidence | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<{ items: Evidence[] }>("/evidence", { limit: 50 })
      .then((d) => setEvidence(d.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="flex h-full gap-4">
      <div className="w-96 bg-forest-800 rounded-xl border border-forest-700 flex flex-col">
        <div className="p-4 border-b border-forest-700 font-semibold">Evidence ({evidence.length})</div>
        <div className="flex-1 overflow-y-auto divide-y divide-forest-700">
          {evidence.map((ev) => (
            <button
              key={ev.id}
              onClick={() => setSelected(ev)}
              className={`w-full text-left p-3 hover:bg-forest-700 ${
                selected?.id === ev.id ? "bg-forest-700" : ""
              }`}
            >
              <div className="text-sm font-medium text-gray-100 mb-1">
                {ev.sha256.slice(0, 16)}…
              </div>
              <div className="text-xs text-gray-400 flex justify-between">
                <span>{ev.kind}</span>
                <span>{new Date(ev.captured_at).toLocaleString()}</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Camera: {ev.camera_id.slice(0, 8)}…
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1">
        {selected ? (
          <EvidenceViewer evidence={selected} onClose={() => setSelected(null)} />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500">Select evidence to view</div>
        )}
      </div>
    </div>
  );
}

function EvidenceViewer({ evidence, onClose }: { evidence: Evidence; onClose: () => void }) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!evidence) return;
    const url = `${import.meta.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/evidence/${evidence.id}/file`;
    setImageUrl(url);
  }, [evidence.id]);

  return (
    <div className="flex flex-col h-full bg-forest-800 rounded-xl border border-forest-700">
      <div className="flex items-center justify-between p-4 border-b border-forest-700">
        <button onClick={onClose} className="text-gray-400 hover:text-gray-100 mb-1 block">← Back</button>
        <div className="text-right">
          <p className="font-medium text-gray-100">{evidence.sha256.slice(0, 32)}…</p>
          <p className="text-xs text-gray-400">{evidence.kind} • {new Date(evidence.captured_at).toLocaleString()}</p>
        </div>
      </div>
      <div className="flex-1 relative bg-black flex items-center justify-center">
        {imageUrl ? (
          <img src={imageUrl} alt="Evidence" className="max-w-full max-h-full object-contain" />
        ) : (
          <div className="text-gray-500">Loading…</div>
        )}
      </div>
      <div className="p-4 border-t border-forest-700">
        <EvidenceDisclaimer />
        <div className="mt-2 text-xs text-gray-400 font-mono">
          SHA-256: {evidence.sha256}
        </div>
      </div>
    </div>
  );
}