from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.cleanup import start_cleanup_scheduler
from app import auth, channels, home, playlists, search, video


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

app.include_router(auth.router, prefix="/api")
app.include_router(channels.router, prefix="/api")
app.include_router(home.router, prefix="/api")
app.include_router(playlists.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(video.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
