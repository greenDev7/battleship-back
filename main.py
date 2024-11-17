import uvicorn
from fastapi import FastAPI

from db.db import create_tables, initialize_engine

app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    create_tables(engine=initialize_engine())

    uvicorn.run(app, host="0.0.0.0", port=5000)
