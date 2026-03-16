from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.database import engine, Base
from backend.routers.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables ready")
    yield


app = FastAPI(title="HomeSeeker AI", lifespan=lifespan)

app.include_router(chat_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
