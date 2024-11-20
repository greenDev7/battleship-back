import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

from db import create_tables, get_engine
from routers import user, game

app = FastAPI()

origins = [
    # "*",
    "http://127.0.0.1:8080",
]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   # allow_credentials=True,
                   # allow_methods=["*"],
                   # allow_headers=["*"],
                   )

app.include_router(user.router)
app.include_router(game.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/createTables")
async def health_check():
    create_tables(get_engine())


@app.websocket("/ws")
async def websocket_endpoint(w: WebSocket):
    await w.accept()
    try:
        while True:
            data = await w.receive_json()
            print('data:', data)
            await w.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print('Disconnected')


# if __name__ == "__main__":
#     create_tables(get_engine())

    # uvicorn.run(app, host="0.0.0.0", port=5000)
