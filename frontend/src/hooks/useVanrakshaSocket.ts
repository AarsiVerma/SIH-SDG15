"use client";

import { useEffect, useRef, useCallback } from "react";
import { getWSClient, WSClient } from "@/lib/ws";

interface WSMessage {
  topic: string;
  type: string;
  payload: any;
  ts: string;
}

export function useVanrakshaSocket(topics: string[] = ["incidents", "health", "sos", "events"]) {
  const wsRef = useRef<WSClient | null>(null);
  const handlersRef = useRef<Map<string, Set<Function>>>(new Map());

  // Initialize connection
  useEffect(() => {
    const ws = getWSClient(topics);
    wsRef.current = ws;

    ws.connect().catch(console.error);

    return () => {
      // Don't disconnect on unmount to keep singleton alive
    };
  }, [topics.join(",")]);

  // Subscribe to messages
  const subscribe = useCallback((topic: string, handler: (payload: any) => void) => {
    const ws = wsRef.current;
    if (!ws) return () => {};

    const unsubscribe = ws.onMessage((msgTopic, type, payload) => {
      if (msgTopic === topic) {
        handler(payload);
      }
    });

    return unsubscribe;
  }, []);

  // Subscribe to specific topic events
  const onIncidents = useCallback((handler: (payload: any) => void) => subscribe("incidents", handler), [subscribe]);
  const onHealth = useCallback((handler: (payload: any) => void) => subscribe("health", handler), [subscribe]);
  const onSOS = useCallback((handler: (payload: any) => void) => subscribe("sos", handler), [subscribe]);
  const onEvents = useCallback((handler: (payload: any) => void) => subscribe("events", handler), [subscribe]);

  return {
    isConnected: wsRef.current?.isConnected() ?? false,
    onIncidents,
    onHealth,
    onSOS,
    onEvents,
    subscribe,
  };
}