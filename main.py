import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_tables_and_add_initial_data, get_engine
from websocket import route

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

app.include_router(route.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/createTables")
async def initialize_tables():
    await create_tables_and_add_initial_data(get_engine())


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
