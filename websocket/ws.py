# from fastapi import WebSocket
#
# from main import app
#
#
# @app.websocket("/ws")
# async def websocket_endpoint(w: WebSocket):
#     print('##### 1111 ######')
#     await w.accept()
#     print('##### 2222 ######')
#     while True:
#         data = await w.receive_text()
#         await w.send_text(f"Message text was: {data}")
