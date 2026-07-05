"""
Routes de préparation / streaming vidéo.
Le seek fonctionne nativement grâce à Starlette FileResponse (Range headers).
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path as PathParam
from fastapi.responses import FileResponse
from google.oauth2.credentials import Credentials
from pydantic import BaseModel

from app import progress, youtube
from app.downloader import prepare_video, get_status, STATUS_READY, STATUS_ERROR
from app.session import Account, get_active_account, get_credentials

router = APIRouter(prefix="/video", tags=["video"])

# Un ID vidéo YouTube fait toujours 11 caractères [A-Za-z0-9_-]. On le
# contraint ici : video_id finit dans un chemin de fichier (downloader.py)
# et dans l'URL passée à yt-dlp — sans ça, une valeur du style
# "../../etc/passwd" ouvrirait une traversée de répertoire (lecture/écriture
# de fichier arbitraire via prepare/stream).
VideoId = PathParam(..., pattern=r"^[A-Za-z0-9_-]{11}$")


class ProgressBody(BaseModel):
    position: float
    duration: float


class WatchedBody(BaseModel):
    watched: bool


@router.get("/{video_id}/info")
async def info(video_id: str = VideoId, account: Account = Depends(get_active_account)):
    """Métadonnées (titre, chaîne, date, description…) affichées sous le lecteur."""
    details = await youtube.get_video_details(account.credentials, account.id, video_id)
    if details is None:
        raise HTTPException(status_code=404, detail="Vidéo introuvable.")
    return details


@router.get("/progress")
async def bulk_progress(ids: str, account: Account = Depends(get_active_account)):
    """Progression pour plusieurs vidéos en un seul appel (une requête par
    grille de vignettes, pas une par vignette)."""
    video_ids = [v for v in ids.split(",") if v]
    return await progress.get_progress_bulk(account.id, video_ids)


@router.put("/{video_id}/progress")
async def set_progress(body: ProgressBody, video_id: str = VideoId, account: Account = Depends(get_active_account)):
    await progress.save_progress(account.id, video_id, body.position, body.duration)
    return {"ok": True}


@router.put("/{video_id}/watched")
async def set_watched(body: WatchedBody, video_id: str = VideoId, account: Account = Depends(get_active_account)):
    await progress.mark_watched(account.id, video_id, body.watched)
    return {"ok": True}


@router.post("/{video_id}/prepare")
async def prepare(background_tasks: BackgroundTasks, video_id: str = VideoId, _: Credentials = Depends(get_credentials)):
    """Déclenche le téléchargement en tâche de fond, répond immédiatement."""
    background_tasks.add_task(prepare_video, video_id)
    return {"video_id": video_id, "status": "queued"}


@router.get("/{video_id}/status")
async def status(video_id: str = VideoId, _: Credentials = Depends(get_credentials)):
    return await get_status(video_id)


@router.get("/{video_id}/stream")
async def stream(video_id: str = VideoId, _: Credentials = Depends(get_credentials)):
    st = await get_status(video_id)
    if st.get("state") != STATUS_READY:
        raise HTTPException(status_code=409, detail=f"Vidéo pas prête (état: {st.get('state', 'unknown')})")

    path = st["path"]
    return FileResponse(path, media_type="video/mp4", filename=f"{video_id}.mp4")
