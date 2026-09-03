"""WebSocket hub for real-time updates."""
import json
import asyncio
from typing import Set, Dict, List
from uuid import UUID
from datetime import datetime

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {
            "incidents": set(),
            "health": set(),
            "sos": set(),
            "events": set(),
        }

    async def connect(self, websocket: WebSocket, topics: List[str]):
        await websocket.accept()
        for topic in topics:
            if topic in self.active:
                self.active[topic].add(websocket)

    def disconnect(self, websocket: WebSocket):
        for topic, conns in self.active.items():
            if websocket in conns:
                conns.discard(websocket)

    async def broadcast(self, topic: str, message: dict):
        """Broadcast message to all connections on a topic."""
        if topic not in self.active:
            return

        payload = json.dumps({
            "topic": topic,
            "type": message.get("type", "update"),
            "payload": message,
            "ts": datetime.utcnow().isoformat() + "Z",
        })

        dead = set()
        for ws in self.active[topic]:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)

        for ws in dead:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            self.disconnect(websocket)


# Global hub instance
hub = ConnectionManager()