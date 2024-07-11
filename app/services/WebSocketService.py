from fastapi import WebSocket
from typing import List
from . import LetterService

class WebSocketService:
    connections: List[WebSocket] = []

    @classmethod
    async def connect(cls, websocket: WebSocket):
        await websocket.accept()
        cls.connections.append(websocket)
        return

    @classmethod
    def disconnect(cls, websocket: WebSocket):
        cls.connections.remove(websocket)
        return

    @classmethod
    async def send(cls, *, json: dict, websocket: WebSocket):
        await websocket.send_json(json)
        return

    @classmethod
    async def broadcast(cls, json: dict):
        for connection in cls.connections:
            await connection.send_json(json)
        return

    @classmethod
    async def broadcastLetter(cls, id: int):
        letter = await LetterService.getLetter(id)
        if not letter:
            return
        await cls.broadcast({"type": "new_ltl_letter", "data": letter.model_dump()})
        return