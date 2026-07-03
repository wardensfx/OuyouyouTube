"""
Purge les fichiers vidéo du cache plus vieux que video_ttl_seconds.
APScheduler standard, pas de cron custom à gérer côté OS.
"""
import time
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

logger = logging.getLogger("ytpwa.cleanup")


def _purge_old_files():
    now = time.time()
    count = 0
    for f in settings.cache_dir.glob("*.mp4"):
        if now - f.stat().st_mtime > settings.video_ttl_seconds:
            f.unlink(missing_ok=True)
            count += 1
    if count:
        logger.info("Cleanup: %d fichier(s) supprimé(s)", count)


def start_cleanup_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(_purge_old_files, "interval", seconds=settings.cleanup_interval_seconds)
    scheduler.start()
    return scheduler
