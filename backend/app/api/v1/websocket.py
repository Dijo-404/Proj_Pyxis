"""Local real-time event stream."""

from fastapi import APIRouter, WebSocket

router = APIRouter(tags=["events"])


@router.websocket("/events")
async def event_stream(websocket: WebSocket) -> None:
    """Accept a local client and confirm the event channel is available."""
    await websocket.accept()
    await websocket.send_json({"type": "connected"})
    await websocket.close()
