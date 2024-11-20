from fastapi import WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect


router = APIRouter(
    tags=["WebSocket"],
    responses={404: {"description": "Not found"}},
)


@router.websocket_route("/ws")
async def websocket_endpoint(w: WebSocket):
    await w.accept()
    try:
        while True:
            data = await w.receive_json()
            print('data:', data)
            await w.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print('Disconnected')
