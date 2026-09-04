"use client";

import { useEffect } from "react";
import { MAP_MARKERS } from "@/types/dashboard";
import {
  MapContainer,
  TileLayer,
  Polygon,
  Marker,
  Tooltip,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const RANTHAMBORE_CENTER = [26.0173, 76.5026] as [number, number];
const RANTHAMBORE_BOUNDS = [
  [25.97, 76.45],
  [26.06, 76.56],
] as [[number, number], [number, number]];

const SECTOR_BOUNDARY = [
  [26.03, 76.48],
  [26.05, 76.5],
  [26.04, 76.53],
  [26.01, 76.54],
  [25.99, 76.52],
  [25.98, 76.49],
] as [number, number][];

function percentageToLatLng(x: number, y: number): [number, number] {
  const latRange = RANTHAMBORE_BOUNDS[1][0] - RANTHAMBORE_BOUNDS[0][0];
  const lngRange = RANTHAMBORE_BOUNDS[1][1] - RANTHAMBORE_BOUNDS[0][1];
  return [
    RANTHAMBORE_BOUNDS[1][0] - (y / 100) * latRange,
    RANTHAMBORE_BOUNDS[0][1] + (x / 100) * lngRange,
  ];
}

function MapLayerControls() {
  const map = useMap();

  useEffect(() => {
    map.setMaxBounds(L.latLngBounds(RANTHAMBORE_BOUNDS));
  }, [map]);

  return null;
}

function MapMarkers({ onMarkerClick }: { onMarkerClick: (position: [number, number], label: string) => void }) {
  return (
    <>
      {MAP_MARKERS.map((marker) => {
        const position = percentageToLatLng(marker.x, marker.y);

        const getMarkerHtml = (type: string) => {
          const isAlert = type === "alert";
          const isCamera = type === "camera";
          const isPatrol = type === "patrol";
          const bgClass = isAlert
            ? "bg-red-600 text-white animate-pulse"
            : isCamera
            ? "bg-emerald-600 text-white"
            : isPatrol
            ? "bg-blue-600 text-white"
            : "bg-[#C08A3E] text-white";
          const svg = isAlert
            ? '<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>'
            : isCamera
            ? '<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 002 2z" /></svg>'
            : isPatrol
            ? '<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" /></svg>'
            : '<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /></svg>';
          return `<div class="flex h-6 w-6 items-center justify-center rounded-full shadow-md transition-transform hover:scale-125 ${bgClass}">${svg}</div>`;
        };

        return (
          <Marker
            key={marker.id}
            position={position}
            icon={L.divIcon({
              className: "custom-marker",
              html: getMarkerHtml(marker.type),
              iconSize: [24, 24],
              iconAnchor: [12, 12],
            })}
            eventHandlers={{
              click: (e: L.LeafletMouseEvent) => {
                e.originalEvent.stopPropagation();
                onMarkerClick(position, marker.label);
              },
            }}
          >
            <Tooltip
              direction="top"
              offset={[0, -10]}
              opacity={0.9}
              className="custom-tooltip"
            >
              <div className="bg-black/90 text-white px-2 py-1 rounded text-[10px] whitespace-nowrap shadow-lg backdrop-blur-sm">
                {marker.label}
              </div>
            </Tooltip>
          </Marker>
        );
      })}
    </>
  );
}

export function LeafletMap({ onMarkerClick }: { onMarkerClick: (position: [number, number], label: string) => void }) {
  return (
    <MapContainer
      center={RANTHAMBORE_CENTER}
      zoom={12}
      maxBounds={RANTHAMBORE_BOUNDS}
      maxZoom={16}
      minZoom={10}
      style={{ width: "100%", height: "100%" }}
      scrollWheelZoom={true}
      doubleClickZoom={true}
      touchZoom={true}
      attributionControl={false}
    >
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attribution="&copy; <a href='https://www.esri.com/'>Esri</a> &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
        maxZoom={19}
      />
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
        attribution=""
        maxZoom={19}
        pane="overlayPane"
      />

      <Polygon
        positions={SECTOR_BOUNDARY}
        color="#C08A3E"
        weight={2}
        dashArray="10, 10"
        fillColor="#C08A3E"
        fillOpacity={0.05}
        interactive={false}
      />

      <MapMarkers onMarkerClick={onMarkerClick} />
      <MapLayerControls />
    </MapContainer>
  );
}