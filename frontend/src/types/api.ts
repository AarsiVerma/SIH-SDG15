/** API type definitions matching backend schemas. */
export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Camera {
  id: string;
  name: string;
  code: string;
  forest_id: string | null;
  location: { type: "Point"; coordinates: [number, number] };
  heading_deg: number | null;
  status: "planned" | "active" | "offline" | "retired" | "degraded";
  is_simulated: boolean;
  created_at: string;
  updated_at: string;
  sources: CameraSource[];
}

export interface CameraSource {
  id: string;
  camera_id: string;
  source_type: "file" | "webcam" | "rtsp" | "other";
  uri: string;
  extra: Record<string, any>;
  created_at: string;
}

export interface Zone {
  id: string;
  forest_id: string;
  name: string;
  zone_type: "patrol" | "restricted" | "corridor" | "buffer" | "other";
  is_restricted: boolean;
  geom: { type: "Polygon"; coordinates: number[][][] };
  created_at: string;
  updated_at: string;
}

export interface ForestArea {
  id: string;
  name: string;
  geom: { type: "Polygon"; coordinates: number[][][] };
  created_at: string;
  updated_at: string;
}

export interface Ranger {
  id: string;
  badge_code: string;
  name: string;
  is_simulated: boolean;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Detection {
  id: string;
  camera_id: string;
  frame_seq: number;
  captured_at: string;
  class_name: string;
  class_id: number;
  confidence: number;
  bbox_xyxy: { x1: number; y1: number; x2: number; y2: number };
  centroid: { type: "Point"; coordinates: [number, number] } | null;
  track_id: string | null;
  detector_id: string;
  model_version: string;
}

export interface Track {
  id: string;
  camera_id: string;
  local_track_id: number;
  class_name: string;
  first_seen: string;
  last_seen: string;
  confidence_avg: number;
  status: "active" | "ended";
  global_id: string | null;
}

export interface TrackPoint {
  id: string;
  track_id: string;
  captured_at: string;
  bbox_xyxy: { x1: number; y1: number; x2: number; y2: number };
  centroid_image: { x: number; y: number };
  map_point: { type: "Point"; coordinates: [number, number] } | null;
}

export interface Event {
  id: string;
  camera_id: string;
  event_type: string;
  language_key: string;
  correlation_key: string;
  window_start: string;
  window_end: string;
  location: { type: "Point"; coordinates: [number, number] };
  risk_score: number | null;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | null;
  payload: Record<string, any>;
  alertable: boolean;
  created_at: string;
}

export interface EventFactor {
  code: string;
  delta: number;
  reason: string;
}

export interface Incident {
  id: string;
  public_id: string;
  title: string;
  language_key: string;
  status: "NEW" | "ACKNOWLEDGED" | "INVESTIGATING" | "DISPATCHED" | "RESOLVED" | "CLOSED";
  risk_score: number | null;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | null;
  location: { type: "Point"; coordinates: [number, number] };
  assigned_user_id: string | null;
  resolution_notes: string | null;
  created_at: string;
  updated_at: string;
  events: Event[];
  evidence: Evidence[];
}

export interface IncidentDetail extends Incident {
  factors: EventFactor[];
  status_history: StatusHistory[];
}

export interface StatusHistory {
  id: string;
  incident_id: string;
  from_status: string | null;
  to_status: string;
  actor_user_id: string | null;
  note: string | null;
  at: string;
}

export interface Evidence {
  id: string;
  incident_id: string | null;
  event_id: string | null;
  camera_id: string;
  kind: "frame" | "clip" | "json";
  storage_uri: string;
  sha256: string;
  captured_at: string;
  bbox_xyxy: { x1: number; y1: number; x2: number; y2: number } | null;
  disclaimer_key: string;
}

export interface WildlifeObservation {
  id: string;
  track_id: string;
  camera_id: string;
  species: string;
  count_estimate: number;
  first_seen: string;
  last_seen: string;
  location: { type: "Point"; coordinates: [number, number] };
}

export interface FireEvent {
  id: string;
  camera_id: string;
  event_type: string;
  severity: string;
  location: { type: "Point"; coordinates: [number, number] };
  created_at: string;
}

export interface NearbyAsset {
  type: "ranger" | "camera";
  id: string;
  name: string;
  location: { type: "Point"; coordinates: [number, number] };
}

export interface DashboardSummary {
  open_incidents: number;
  incidents_by_level: Record<string, number>;
  cameras_online: number;
  cameras_total: number;
  rangers_active: number;
  last_sos_at: string | null;
}

export interface RiskAssessment {
  score: number;
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  factors: EventFactor[];
  requires_human_verification: boolean;
}

export interface TaxonomyClass {
  class_name: string;
  class_id: number;
  display_name: string;
  language_key: string | null;
  layer: string;
}