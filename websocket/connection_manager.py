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

    async def send_personal_message(self, client_uuid: uuid.UUID, message: dict):
        if client_uuid in self.active_connections:
            await self.active_connections[client_uuid].send_json(message)

    async def send_structured_data(self, client_uuid: uuid.UUID, msg_type: str, data: dict, is_status_ok: bool = True):
        message_to_send = {'msg_type': msg_type, 'data': data, 'is_status_ok': is_status_ok}
        await self.send_personal_message(client_uuid, message_to_send)

    async def broadcast(self, message: str):  # но использовать широковещательную рассылку пока не планировал
        for connection in self.active_connections.values():
            await connection.send_text(message)

    def print_clients(self):
        print('Clients: ', self.active_connections.keys())
