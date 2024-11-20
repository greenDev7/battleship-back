from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_tables, get_engine
from routers import user, game
from websocket import ws

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
app.include_router(ws.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/createTables")
async def health_check():
    create_tables(get_engine())
