import uuid

from fastapi import WebSocket, APIRouter, WebSocketDisconnect

from controllers.ws.main_controller import process_data
from websocket.connection_manager import ConnectionManager

router = APIRouter(
    tags=["WebSocket"],
    responses={404: {"description": "Not found"}},
)

manager = ConnectionManager()


@router.websocket("/client/{client_uuid}/ws")
async def websocket_endpoint(ws: WebSocket, client_uuid: uuid.UUID):
    await manager.connect(client_uuid, ws)
    try:
        while True:
            data_from_client = await ws.receive_json()
            await process_data(client_uuid, data_from_client, manager)
    except WebSocketDisconnect:
        manager.disconnect(client_uuid)
        manager.print_clients()
