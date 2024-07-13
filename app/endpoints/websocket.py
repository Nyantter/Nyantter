from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services import WebSocketService

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await WebSocketService.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await WebSocketService.send(
                json={"detail": "connected"}, websocket=websocket
            )
    except WebSocketDisconnect:
        WebSocketService.disconnect(websocket)
