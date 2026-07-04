"""
Récupération du flux vidéo via yt-dlp (import direct de la lib, pas de subprocess).
Le fichier est écrit dans cache_dir puis servi via FileResponse (Range natif),
puis supprimé par le job de nettoyage (app/cleanup.py).
"""
import asyncio
import time
from pathlib import Path

import yt_dlp

from app.cache import get_redis
from app.config import settings

STATUS_DOWNLOADING = "downloading"
STATUS_READY = "ready"
STATUS_ERROR = "error"


def _status_key(video_id: str) -> str:
    return f"video_status:{video_id}"


def _output_path(video_id: str) -> Path:
    return settings.cache_dir / f"{video_id}.mp4"


async def get_status(video_id: str) -> dict:
    raw = await get_redis().hgetall(_status_key(video_id))
    return raw or {"state": "unknown"}


async def _set_status(video_id: str, **fields):
    await get_redis().hset(_status_key(video_id), mapping=fields)
    await get_redis().expire(_status_key(video_id), settings.video_ttl_seconds + 60)


def _run_ytdlp(video_id: str, loop: asyncio.AbstractEventLoop) -> Path:
    """Bloquant — à exécuter dans un thread (run_in_executor). Le hook de
    progression tourne dans ce même thread ; on repasse par
    run_coroutine_threadsafe pour toucher Redis (client async) depuis la
    boucle asyncio principale."""
    output_path = _output_path(video_id)

    def on_progress(d):
        if d.get("status") != "downloading":
            return
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        downloaded = d.get("downloaded_bytes")
        if not total or not downloaded:
            return
        percent = round(downloaded / total * 100)
        asyncio.run_coroutine_threadsafe(
            _set_status(video_id, state=STATUS_DOWNLOADING, progress=str(percent)), loop
        )

    ydl_opts = {
        "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(output_path.with_suffix("")) + ".%(ext)s",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "progress_hooks": [on_progress],
    }
    if settings.ytdlp_cookies_file:
        ydl_opts["cookiefile"] = settings.ytdlp_cookies_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

    if not output_path.exists():
        raise FileNotFoundError(f"yt-dlp n'a pas produit {output_path}")
    return output_path


async def prepare_video(video_id: str):
    """Lance le téléchargement si pas déjà en cache, met à jour le statut Redis."""
    output_path = _output_path(video_id)
    if output_path.exists():
        await _set_status(video_id, state=STATUS_READY, path=str(output_path), ts=str(time.time()))
        return

    current = await get_status(video_id)
    if current.get("state") == STATUS_DOWNLOADING:
        return  # déjà en cours, on ne relance pas

    await _set_status(video_id, state=STATUS_DOWNLOADING, progress="0", ts=str(time.time()))
    try:
        loop = asyncio.get_running_loop()
        path = await loop.run_in_executor(None, _run_ytdlp, video_id, loop)
        await _set_status(video_id, state=STATUS_READY, path=str(path), ts=str(time.time()))
    except Exception as exc:
        await _set_status(video_id, state=STATUS_ERROR, error=str(exc), ts=str(time.time()))
        raise
