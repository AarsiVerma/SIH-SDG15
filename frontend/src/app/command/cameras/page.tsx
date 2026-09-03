"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Camera } from "@/types/api";

export default function CamerasPage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selected, setSelected] = useState<Camera | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<{ items: Camera[] }>("/cameras", { limit: 50 })
      .then((d) => setCameras(d.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="flex h-full gap-4">
      <div className="w-96 bg-forest-800 rounded-xl border border-forest-700 flex flex-col">
        <div className="p-4 border-b border-forest-700 font-semibold">Cameras ({cameras.length})</div>
        <div className="flex-1 overflow-y-auto divide-y divide-forest-700">
          {cameras.map((cam) => (
            <button
              key={cam.id}
              onClick={() => setSelected(cam)}
              className={`w-full text-left p-3 hover:bg-forest-700 ${
                selected?.id === cam.id ? "bg-forest-700" : ""
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium">{cam.name}</span>
                <span
                  className={`px-2 py-0.5 rounded text-xs ${
                    cam.status === "active" ? "bg-green-900/50 text-green-300" : "bg-gray-700 text-gray-300"
                  }`}
                >
                  {cam.status}
                </span>
              </div>
              <div className="text-xs text-gray-400">{cam.code}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1">
        {selected ? (
          <CameraViewer camera={selected} onClose={() => setSelected(null)} />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500">Select a camera</div>
        )}
      </div>
    </div>
  );
}

function CameraViewer({ camera, onClose }: { camera: Camera; onClose: () => void }) {
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!camera) return;
    setLoading(true);
    fetch(`${import.meta.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/cameras/${camera.id}/preview`)
      .then(r => r.blob())
      .then(blob => URL.createObjectURL(blob))
      .then(setPreview)
      .catch(() => setPreview(null))
      .finally(() => setLoading(false));
  }, [camera.id]);

  return (
    <div className="flex flex-col h-full bg-forest-800 rounded-xl border border-forest-700">
      <div className="flex items-center justify-between p-4 border-b border-forest-700">
        <div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-100 mb-1 block">← Back</button>
          <h2 className="font-semibold">{camera.name}</h2>
          <p className="text-sm text-gray-400">{camera.code} • {camera.status}</p>
        </div>
      </div>
      <div className="flex-1 relative bg-black">
        {loading && <div className="absolute inset-0 flex items-center justify-center text-gray-500">Loading…</div>}
        {preview ? (
          <img src={preview} alt="Camera preview" className="w-full h-full object-contain" />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No preview available (simulated file source)
          </div>
        )}
      </div>
    </div>
  );
}