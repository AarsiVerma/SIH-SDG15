"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useVanrakshaSocket } from "@/hooks/useVanrakshaSocket";
import { fetchGeoJSON } from "@/lib/geo";
import { FeatureCollection } from "@/lib/geo";

// Dynamically import Leaflet-dependent components with SSR disabled
const ForestMap = dynamic(() => import("@/components/map/ForestMap").then((mod) => mod.default), {
  ssr: false,
  loading: () => <div className="flex h-full items-center justify-center bg-forest-900 text-gray-400">Loading map…</div>,
});

const LayerToggle = dynamic(() => import("@/components/map/LayerToggle").then((mod) => mod.default), {
  ssr: false,
  loading: () => null,
});

export default function MapPage() {
  const [layers, setLayers] = useState<Record<string, FeatureCollection>>({});
  const [leafletMap, setLeafletMap] = useState<any>(null);

  const { onIncidents, onHealth, onSOS, isConnected } = useVanrakshaSocket([
    "incidents",
    "health",
    "sos",
    "events",
  ]);

  useEffect(() => {
    const unsubscribeIncidents = onIncidents(() => {
      fetchGeoJSON("/geo/incidents").then((fc) => setLayers((prev) => ({ ...prev, incidents: fc })));
    });
    const unsubscribeHealth = onHealth(() => {
      fetchGeoJSON("/geo/cameras").then((fc) => setLayers((prev) => ({ ...prev, cameras: fc })));
    });
    const unsubscribeSOS = onSOS(() => {});

    return () => {
      unsubscribeIncidents();
      unsubscribeHealth();
      unsubscribeSOS();
    };
  }, [onIncidents, onHealth, onSOS]);

  useEffect(() => {
    const endpoints = [
      { key: "forests", url: "/geo/forests" },
      { key: "zones", url: "/geo/zones" },
      { key: "cameras", url: "/geo/cameras" },
      { key: "incidents", url: "/geo/incidents" },
      { key: "rangers", url: "/geo/rangers" },
      { key: "wildlife", url: "/geo/wildlife" },
      { key: "fire", url: "/geo/fire" },
    ];

    Promise.all(
      endpoints.map(({ key, url }) => fetchGeoJSON(url).then((fc) => ({ key, fc })))
    ).then((results) => {
      const layerMap: Record<string, FeatureCollection> = {};
      results.forEach(({ key, fc }) => { layerMap[key] = fc; });
      setLayers(layerMap);
    }).catch(console.error);
  }, []);

  const handleMapReady = (map: any) => {
    setLeafletMap(map);
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-forest-900">
      <div className="flex-1 relative">
        <ForestMap
          initialCenter={[77.25, 12.25]}
          initialZoom={11}
          onMapClick={() => {}}
          onMapReady={handleMapReady}
        />
        <div className="absolute top-4 right-4 z-10">
          <span className={`flex items-center gap-1 px-2 py-1 rounded text-xs bg-forest-800 border border-forest-700 ${isConnected ? "text-green-400" : "text-red-400"}`}>
            {isConnected ? "● LIVE" : "● OFFLINE"}
          </span>
        </div>
      </div>

      <LayerToggle map={leafletMap} layers={layers} />
    </div>
  );
}