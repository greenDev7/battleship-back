import uuid

from fastapi import WebSocket, APIRouter, WebSocketDisconnect

from controllers.ws.main_controller import process_data
from websocket.connection_manager import ConnectionManager

router = APIRouter(
    tags=["WebSocket"],
    responses={404: {"description": "Not found"}},
)

manager = ConnectionManager()


@router.websocket_route("/client/{client_uuid}/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect()
    try:
        while True:
            data_from_client = await ws.receive_json()
            data_for_client = await process_data(data_from_client)
            print('data_from_client:', data_from_client)
            print('data_for_client:', data_for_client)
            await ws.send_text(data_for_client)
    except WebSocketDisconnect:
        manager.disconnect(ws)
        manager.print_clients()
