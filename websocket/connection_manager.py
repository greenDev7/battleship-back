import uuid

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[uuid.UUID, WebSocket] = {}

    async def connect(self, client_uuid: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_uuid] = websocket

    def disconnect(self, client_uuid: uuid.UUID):
        self.active_connections.pop(client_uuid)

    async def send_personal_message(self, message: str, client_uuid: uuid.UUID):
        if client_uuid in self.active_connections:
            await self.active_connections[client_uuid].send_text(message)

    async def broadcast(self, message: str):  # но использовать широковещательную рассылку пока не планировал
        for connection in self.active_connections.values():
            await connection.send_text(message)
