"""
Routes de préparation / streaming vidéo.
Le seek fonctionne nativement grâce à Starlette FileResponse (Range headers).
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from google.oauth2.credentials import Credentials

from app.downloader import prepare_video, get_status, STATUS_READY, STATUS_ERROR
from app.session import get_credentials

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/{video_id}/prepare")
async def prepare(video_id: str, background_tasks: BackgroundTasks, _: Credentials = Depends(get_credentials)):
    """Déclenche le téléchargement en tâche de fond, répond immédiatement."""
    background_tasks.add_task(prepare_video, video_id)
    return {"video_id": video_id, "status": "queued"}


@router.get("/{video_id}/status")
async def status(video_id: str, _: Credentials = Depends(get_credentials)):
    return await get_status(video_id)


@router.get("/{video_id}/stream")
async def stream(video_id: str, _: Credentials = Depends(get_credentials)):
    st = await get_status(video_id)
    if st.get("state") != STATUS_READY:
        raise HTTPException(status_code=409, detail=f"Vidéo pas prête (état: {st.get('state', 'unknown')})")

    path = st["path"]
    return FileResponse(path, media_type="video/mp4", filename=f"{video_id}.mp4")
