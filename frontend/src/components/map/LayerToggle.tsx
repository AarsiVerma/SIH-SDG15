"use client";

import { useState, useEffect } from "react";
import { LAYER_CONFIGS, MapLayerConfig, createGeoJSONLayer } from "./layers";
import { FeatureCollection } from "@/lib/geo";
import L from "leaflet";

interface LayerToggleProps {
  map: L.Map | null;
  layers: Record<string, FeatureCollection>;
  onLayerSelect?: (layerId: string, feature: any) => void;
}

export default function LayerToggle({ map, layers, onLayerSelect }: LayerToggleProps) {
  const [visibleLayers, setVisibleLayers] = useState<Record<string, boolean>>(
    LAYER_CONFIGS.reduce((acc, c) => ({ ...acc, [c.id]: c.visible }), {})
  );
  const [layerInstances, setLayerInstances] = useState<Record<string, L.GeoJSON>>({});

  // Toggle layer visibility
  const toggleLayer = (layerId: string) => {
    setVisibleLayers((prev) => {
      const next = { ...prev, [layerId]: !prev[layerId] };
      return next;
    });
  };

  // Load layer when it becomes visible
  useEffect(() => {
    if (!map) return;

    Object.entries(visibleLayers).forEach(([layerId, isVisible]) => {
      const config = LAYER_CONFIGS.find((c) => c.id === layerId);
      if (!config) return;

      const geojson = layers[layerId];
      if (!geojson) return;

      if (isVisible && !layerInstances[layerId]) {
        const layer = createGeoJSONLayer(geojson, config);
        if (config.onEachFeature) {
          layer.on("click", (e: any) => {
            onLayerSelect?.(layerId, e.layer.feature);
          });
        }
        layer.addTo(map);
        setLayerInstances((prev) => ({ ...prev, [layerId]: layer }));
      } else if (!isVisible && layerInstances[layerId]) {
        map.removeLayer(layerInstances[layerId]);
        setLayerInstances((prev) => {
          const next = { ...prev };
          delete next[layerId];
          return next;
        });
      }
    });
  }, [visibleLayers, map, layerInstances, layers]);

  return (
    <div className="bg-forest-800 rounded-lg p-4 border border-forest-700">
      <h3 className="font-semibold mb-3 text-gray-100">Map Layers</h3>
      <div className="space-y-2">
        {LAYER_CONFIGS.map((layer) => (
          <label key={layer.id} className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={visibleLayers[layer.id]}
              onChange={() => toggleLayer(layer.id)}
              className="w-4 h-4 accent-forest-500"
            />
            <span className="text-gray-200">{layer.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}