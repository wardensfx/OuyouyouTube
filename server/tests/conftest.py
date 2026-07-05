import fakeredis
import pytest

from app import cache


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Redis en mémoire pour chaque test (pas de service externe requis) —
    remplace le singleton module-level de cache.py avant toute résolution
    de get_redis()."""
    client = fakeredis.FakeAsyncRedis(decode_responses=True)
    monkeypatch.setattr(cache, "_redis", client)
    return client
