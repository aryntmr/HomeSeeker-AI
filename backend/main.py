from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables ready")
    yield


app = FastAPI(title="HomeSeeker AI", lifespan=lifespan)

# Routers added in Phase 4

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
