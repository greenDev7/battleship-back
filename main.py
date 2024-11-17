import uvicorn
from fastapi import FastAPI

from routers import user, game

app = FastAPI()

app.include_router(user.router)
app.include_router(game.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    # create_tables(engine=engine)

    uvicorn.run(app, host="0.0.0.0", port=5000)
