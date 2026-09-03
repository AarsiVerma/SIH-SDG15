/** Geo utilities for frontend. */
export interface GeoJSONPoint {
  type: "Point";
  coordinates: [number, number];
}

export interface GeoJSONPolygon {
  type: "Polygon";
  coordinates: number[][][];
}

export interface Feature<T = any> {
  type: "Feature";
  geometry: GeoJSONPoint | GeoJSONPolygon | null;
  properties: T;
}

export interface FeatureCollection<T = any> {
  type: "FeatureCollection";
  features: Feature<T>[];
}

export const DEFAULT_CENTER: [number, number] = [77.25, 12.25];
export const DEFAULT_ZOOM = 11;

export async function fetchGeoJSON<T>(endpoint: string): Promise<FeatureCollection<T>> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1${endpoint}`);
  if (!response.ok) throw new Error(`Failed to fetch ${endpoint}`);
  return response.json();
}