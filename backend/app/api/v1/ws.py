"""WebSocket API endpoint."""
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from uuid import UUID

from app.ws.hub import hub

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    topics: List[str] = Query(default=["incidents", "health", "sos", "events"]),
):
    """Connect to real-time updates."""
    await hub.connect(websocket, topics)
    try:
        while True:
            # Keep alive - could parse incoming messages for subscriptions
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)