export interface CameraFeed {
  id: string;
  name: string;
  location: string;
  zone: string;
  status: "live" | "offline" | "alert";
  alertType?: "tiger" | "human" | "fire" | "vehicle" | "elephant";
  alertMessage?: string;
  imageUrl: string;
}

export interface AIAlert {
  id: string;
  title: string;
  zone: string;
  location: string;
  time: string;
  priority: "High" | "Medium" | "Low";
  category: "Wildlife" | "Intrusion" | "Fire" | "Vehicle";
  imageUrl: string;
}

export interface MapMarker {
  id: string;
  type: "camera" | "alert" | "patrol" | "checkpoint";
  label: string;
  x: number; // percentage on map
  y: number; // percentage on map
  status?: string;
}

export interface ActivityStat {
  name: string;
  count: number;
  percentage: number;
  color: string;
}

export const INITIAL_CAMERAS: CameraFeed[] = [
  {
    id: "cam-2a",
    name: "Camera 2A - Waterhole",
    location: "Zone 2A",
    zone: "Zone 2A",
    status: "live",
    imageUrl: "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-3f",
    name: "Camera 3F - Ridge Trail",
    location: "Ridge Trail",
    zone: "Zone 3F",
    status: "alert",
    alertType: "tiger",
    alertMessage: "Tiger Detected",
    imageUrl: "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-1b",
    name: "Camera 1B - Salt Lick",
    location: "Salt Lick",
    zone: "Zone 1B",
    status: "live",
    imageUrl: "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-4d",
    name: "Camera 4D - Forest Road",
    location: "Forest Road",
    zone: "Zone 4D",
    status: "live",
    imageUrl: "https://images.unsplash.com/photo-1533587851505-d119e13fa0d7?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-7c",
    name: "Camera 7C - Grassland",
    location: "Grassland",
    zone: "Zone 7C",
    status: "live",
    imageUrl: "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-5a",
    name: "Camera 5A - Stream",
    location: "Stream",
    zone: "Zone 5A",
    status: "live",
    imageUrl: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-9b",
    name: "Camera 9B - Hill Top",
    location: "Hill Top",
    zone: "Zone 9B",
    status: "live",
    imageUrl: "https://images.unsplash.com/photo-1425913397330-cf8af2ff40a1?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-6e",
    name: "Camera 6E - Boundary",
    location: "Boundary",
    zone: "Zone 6E",
    status: "alert",
    alertType: "human",
    alertMessage: "Human Intrusion",
    imageUrl: "https://images.unsplash.com/photo-1516214104703-d870798883c5?w=800&q=80&auto=format&fit=crop",
  },
  {
    id: "cam-11d",
    name: "Camera 11D - Fire Watch",
    location: "Fire Watch",
    zone: "Zone 11D",
    status: "alert",
    alertType: "fire",
    alertMessage: "Smoke Detected",
    imageUrl: "https://images.unsplash.com/photo-1517594422361-5eeb8ae275a9?w=800&q=80&auto=format&fit=crop",
  },
];

export const INITIAL_ALERTS: AIAlert[] = [
  {
    id: "alert-1",
    title: "Tiger Detected",
    zone: "Zone 3F",
    location: "Ridge Trail",
    time: "10:24 AM",
    priority: "High",
    category: "Wildlife",
    imageUrl: "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=400&q=80&auto=format&fit=crop",
  },
  {
    id: "alert-2",
    title: "Human Intrusion",
    zone: "Zone 6E",
    location: "Boundary",
    time: "10:18 AM",
    priority: "High",
    category: "Intrusion",
    imageUrl: "https://images.unsplash.com/photo-1516214104703-d870798883c5?w=400&q=80&auto=format&fit=crop",
  },
  {
    id: "alert-3",
    title: "Fire / Smoke Detected",
    zone: "Zone 11D",
    location: "Fire Watch",
    time: "10:05 AM",
    priority: "Medium",
    category: "Fire",
    imageUrl: "https://images.unsplash.com/photo-1517594422361-5eeb8ae275a9?w=400&q=80&auto=format&fit=crop",
  },
  {
    id: "alert-4",
    title: "Vehicle Detected",
    zone: "Zone 4D",
    location: "Forest Road",
    time: "09:52 AM",
    priority: "Low",
    category: "Vehicle",
    imageUrl: "https://images.unsplash.com/photo-1533587851505-d119e13fa0d7?w=400&q=80&auto=format&fit=crop",
  },
  {
    id: "alert-5",
    title: "Elephant Herd",
    zone: "Zone 1B",
    location: "Salt Lick",
    time: "09:40 AM",
    priority: "Low",
    category: "Wildlife",
    imageUrl: "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=400&q=80&auto=format&fit=crop",
  },
];

export const MAP_MARKERS: MapMarker[] = [
  { id: "m1", type: "alert", label: "Tiger Detected (Zone 3F)", x: 26, y: 22 },
  { id: "m2", type: "alert", label: "Human Intrusion (Zone 6E)", x: 67, y: 38 },
  { id: "m3", type: "alert", label: "Smoke Detected (Zone 11D)", x: 38, y: 76 },
  { id: "m4", type: "camera", label: "Cam 2A", x: 18, y: 44 },
  { id: "m5", type: "camera", label: "Cam 1B", x: 48, y: 32 },
  { id: "m6", type: "camera", label: "Cam 7C", x: 72, y: 18 },
  { id: "m7", type: "camera", label: "Cam 9B", x: 84, y: 55 },
  { id: "m8", type: "patrol", label: "Patrol Unit 1 (On Duty)", x: 30, y: 78 },
  { id: "m9", type: "patrol", label: "Patrol Unit 2 (On Duty)", x: 58, y: 46 },
  { id: "m10", type: "checkpoint", label: "Checkpoint Alpha", x: 42, y: 90 },
];

export const ACTIVITY_STATS: ActivityStat[] = [
  { name: "Wildlife Sightings", count: 58, percentage: 45, color: "#10B981" },
  { name: "Human Intrusion", count: 22, percentage: 17, color: "#EF4444" },
  { name: "Vehicles", count: 18, percentage: 14, color: "#3B82F6" },
  { name: "Fire / Smoke", count: 12, percentage: 9, color: "#F59E0B" },
  { name: "Others", count: 18, percentage: 15, color: "#6B7280" },
];
