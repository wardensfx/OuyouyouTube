from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.cleanup import start_cleanup_scheduler
from app import auth, home, playlists, search, video


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_cleanup_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="YT-PWA backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(home.router)
app.include_router(playlists.router)
app.include_router(search.router)
app.include_router(video.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
