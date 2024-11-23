import uuid
from fastapi import WebSocket

from controllers.ws.user import create_active_user


async def process_data(client_uuid: uuid.UUID, data_from_client: dict, ws: WebSocket):
    create_active_user(client_uuid, data_from_client, ws.client.host, ws.client.port)
