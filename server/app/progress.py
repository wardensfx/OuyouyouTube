"""
Progression de lecture (position/durée) et statut vu/non-vu, par compte et
par vidéo. Simple hash Redis, pas de TTL — c'est de l'état utilisateur, pas
un cache, indépendant du fichier vidéo lui-même qui reste éphémère (TTL
géré par app/cleanup.py).
"""
import time

from app.cache import get_redis

WATCHED_THRESHOLD = 0.9  # % de la durée à partir duquel on considère "vu"


def _key(account_id: str, video_id: str) -> str:
    return f"progress:{account_id}:{video_id}"


async def save_progress(account_id: str, video_id: str, position: float, duration: float):
    watched = duration > 0 and position / duration >= WATCHED_THRESHOLD
    await get_redis().hset(
        _key(account_id, video_id),
        mapping={
            "position": position,
            "duration": duration,
            "watched": "1" if watched else "0",
            "updated_at": time.time(),
        },
    )


async def mark_watched(account_id: str, video_id: str, watched: bool):
    await get_redis().hset(_key(account_id, video_id), mapping={"watched": "1" if watched else "0"})


async def get_progress(account_id: str, video_id: str) -> dict | None:
    data = await get_redis().hgetall(_key(account_id, video_id))
    if not data:
        return None
    return {
        "position": float(data.get("position", 0)),
        "duration": float(data.get("duration", 0)),
        "watched": data.get("watched") == "1",
    }


async def get_progress_bulk(account_id: str, video_ids: list[str]) -> dict:
    if not video_ids:
        return {}
    redis = get_redis()
    pipe = redis.pipeline()
    for vid in video_ids:
        pipe.hgetall(_key(account_id, vid))
    results = await pipe.execute()

    out = {}
    for vid, data in zip(video_ids, results):
        if not data:
            continue
        out[vid] = {
            "position": float(data.get("position", 0)),
            "duration": float(data.get("duration", 0)),
            "watched": data.get("watched") == "1",
        }
    return out
