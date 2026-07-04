"""
Progression de lecture (position/durée) et statut vu/non-vu, par compte et
par vidéo. Simple hash Redis, pas de TTL — c'est de l'état utilisateur, pas
un cache, indépendant du fichier vidéo lui-même qui reste éphémère (TTL
géré par app/cleanup.py).
"""
import time

from app.cache import get_redis

# Vu si la position atteint (durée - marge), la marge étant la plus petite
# des deux : un ratio de la durée (vidéos courtes, peu de générique à
# sauter) ou un plafond fixe en secondes (vidéos longues, le générique de
# fin dure ~pareil quelle que soit la durée totale).
WATCHED_MIN_RATIO = 0.9
WATCHED_MAX_TAIL_SECONDS = 60


def _is_watched(position: float, duration: float) -> bool:
    if duration <= 0:
        return False
    tail = min(duration * (1 - WATCHED_MIN_RATIO), WATCHED_MAX_TAIL_SECONDS)
    return position >= duration - tail


def _key(account_id: str, video_id: str) -> str:
    return f"progress:{account_id}:{video_id}"


async def save_progress(account_id: str, video_id: str, position: float, duration: float):
    watched = _is_watched(position, duration)
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
