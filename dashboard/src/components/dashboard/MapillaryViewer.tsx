"use client";

import { useEffect, useRef, useState } from "react";
import { Viewer } from "mapillary-js";
import { X, ExternalLink } from "lucide-react";

const MAPillary_ACCESS_TOKEN = "MLY|28069187012721834|8e6b8cc8d9135eeb69dd8a28c80231da";

interface MapillaryViewerProps {
  position: { lat: number; lng: number };
  onClose: () => void;
}

export function MapillaryViewer({ position, onClose }: MapillaryViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const viewer = new Viewer({
      accessToken: MAPillary_ACCESS_TOKEN,
      container: containerRef.current,
      component: {
        cover: false,
        bearing: false,
        zoom: false,
        sequence: false,
      },
    });

    viewerRef.current = viewer;

    // Note: Mapillary Viewer requires an imageId to show imagery
    // In a real implementation, you'd fetch nearby image IDs from Mapillary API
    // For now, we'll show a placeholder and error message if no imageId provided

    return () => {
      viewer.remove();
    };
  }, [position.lat, position.lng]);

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
        <div className="bg-[#0A0F0C] border border-[#233026] rounded-2xl p-6 max-w-md w-full mx-4 text-center">
          <svg className="h-10 w-10 mx-auto mb-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <h3 className="text-lg font-medium text-white mb-2">No Street View Available</h3>
          <p className="text-gray-400 mb-6">Mapillary has no street-level imagery at this location in Ranthambore.</p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-[#C08A3E] text-white rounded-lg hover:bg-[#C08A3E]/90 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="relative w-full h-full max-w-5xl max-h-[80vh] bg-[#0A0F0C] border border-[#233026] rounded-2xl overflow-hidden">
        <div className="absolute top-3 right-3 z-10 flex gap-2">
          <a
            href={`https://www.mapillary.com/app/?lat=${position.lat}&lng=${position.lng}&z=1`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-black/70 rounded-lg text-white hover:bg-black/90 backdrop-blur-sm"
            title="Open in Mapillary"
          >
            <ExternalLink className="h-5 w-5" />
          </a>
          <button
            onClick={onClose}
            className="p-2 bg-black/70 rounded-lg text-white hover:bg-black/90 backdrop-blur-sm"
            title="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div ref={containerRef} className="w-full h-full" style={{ minHeight: "400px" }} />
      </div>
    </div>
  );
}