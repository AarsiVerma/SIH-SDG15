/** Map layer types and utilities. */
import { FeatureCollection } from "@/lib/geo";

export interface MapLayerConfig {
  id: string;
  label: string;
  endpoint: string;
  style: (feature: any) => L.PathOptions;
  onEachFeature?: (feature: any, layer: L.Layer) => void;
  visible: boolean;
}

export const LAYER_CONFIGS: MapLayerConfig[] = [
  {
    id: "forests",
    label: "Forest Areas",
    endpoint: "/geo/forests",
    style: () => ({ color: "#2e8b2e", weight: 2, fillColor: "#2e8b2e", fillOpacity: 0.1 }),
    visible: true,
  },
  {
    id: "zones",
    label: "Zones",
    endpoint: "/geo/zones",
    style: (feature) =>
      feature.properties.is_restricted
        ? { color: "#dc2626", weight: 3, fillColor: "#dc2626", fillOpacity: 0.2, dashArray: "5, 5" }
        : { color: "#3b82f6", weight: 2, fillColor: "#3b82f6", fillOpacity: 0.1 },
    visible: true,
  },
  {
    id: "cameras",
    label: "Cameras",
    endpoint: "/geo/cameras",
    style: (feature) => ({
      radius: 8,
      fillColor: feature.properties.status === "active" ? "#22c55e" : "#ef4444",
      color: "#fff",
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8,
    }),
    onEachFeature: (feature, layer) => {
      layer.bindPopup(`<b>${feature.properties.name}</b><br/>Code: ${feature.properties.code}<br/>Status: ${feature.properties.status}`);
    },
    visible: true,
  },
  {
    id: "incidents",
    label: "Incidents",
    endpoint: "/geo/incidents",
    style: (feature) => {
      const colors: Record<string, string> = {
        CRITICAL: "#dc2626",
        HIGH: "#f97316",
        MEDIUM: "#fbbf24",
        LOW: "#22c55e",
      };
      return {
        radius: 10,
        fillColor: colors[feature.properties.risk_level] || "#6b7280",
        color: "#fff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9,
      };
    },
    onEachFeature: (feature, layer) => {
      layer.bindPopup(`<b>${feature.properties.public_id}</b><br/>${feature.properties.title}<br/>Risk: ${feature.properties.risk_level}`);
    },
    visible: true,
  },
  {
    id: "rangers",
    label: "Rangers",
    endpoint: "/geo/rangers",
    style: () => ({
      radius: 8,
      fillColor: "#3b82f6",
      color: "#fff",
      weight: 2,
      fillOpacity: 0.9,
    }),
    visible: true,
  },
  {
    id: "wildlife",
    label: "Wildlife",
    endpoint: "/geo/wildlife",
    style: () => ({
      radius: 6,
      fillColor: "#f59e0b",
      color: "#fff",
      weight: 2,
      fillOpacity: 0.8,
    }),
    visible: true,
  },
  {
    id: "fire",
    label: "Fire",
    endpoint: "/geo/fire",
    style: () => ({
      radius: 8,
      fillColor: "#ef4444",
      color: "#fff",
      weight: 2,
      fillOpacity: 0.9,
    }),
    visible: true,
  },
];

export function createGeoJSONLayer(geojson: FeatureCollection, config: MapLayerConfig): L.GeoJSON {
  return L.geoJSON(geojson, {
    pointToLayer: (feature, latlng) => {
      const style = config.style(feature);
      if ("radius" in style) {
        return L.circleMarker(latlng, style as L.CircleMarkerOptions);
      }
      return L.polygon(latlng, style as L.PolylineOptions);
    },
    style: (feature) => config.style(feature),
    onEachFeature: config.onEachFeature,
  });
}