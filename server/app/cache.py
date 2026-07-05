"""
Petit wrapper Redis async pour cacher les réponses YouTube Data API
(quota limité, donc on évite de re-hit inutilement).
"""
import json
from redis import asyncio as aioredis

from app.config import settings

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def get_json(key: str):
    raw = await get_redis().get(key)
    return json.loads(raw) if raw else None


async def set_json(key: str, value, ttl: int):
    await get_redis().set(key, json.dumps(value), ex=ttl)


async def delete_prefix(prefix: str):
    """Invalide toutes les clés d'un cache paginé (ex: liked:{account_id}:<page_token>)
    en une fois, plutôt qu'une seule clé fixe."""
    redis = get_redis()
    async for key in redis.scan_iter(match=f"{prefix}*"):
        await redis.delete(key)
