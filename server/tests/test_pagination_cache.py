"""Couvre la construction des clés de cache par page et l'invalidation
`delete_prefix` (SCAN) introduites par la pagination — cf. issue #90 : cette
logique est facile à casser subtilement (un préfixe qui ne correspond plus
exactement) et ne se serait manifestée qu'en production, sous forme de
données obsolètes après une mutation.
"""
from unittest.mock import MagicMock

from app import youtube
from app.cache import delete_prefix


async def test_delete_prefix_removes_only_matching_pages(fake_redis):
    await fake_redis.set("playlist_items:acc1:PL123:", "page0")
    await fake_redis.set("playlist_items:acc1:PL123:tokenA", "page1")
    await fake_redis.set("playlist_items:acc1:PL999:", "unrelated")

    await delete_prefix("playlist_items:acc1:PL123:")

    assert await fake_redis.get("playlist_items:acc1:PL123:") is None
    assert await fake_redis.get("playlist_items:acc1:PL123:tokenA") is None
    assert await fake_redis.get("playlist_items:acc1:PL999:") == "unrelated"


def _video_item(video_id="dQw4w9WgXcQ", next_page_token=None):
    item = {
        "id": video_id,
        "snippet": {
            "title": "titre",
            "channelTitle": "chaîne",
            "channelId": "UCxxxxxxxxxxxxxxxxxxxxxx",
            "thumbnails": {
                "medium": {"url": "https://i.ytimg.com/vi/x/mqdefault.jpg"},
                "default": {"url": "https://i.ytimg.com/vi/x/default.jpg"},
            },
            "publishedAt": "2020-01-01T00:00:00Z",
        },
        "contentDetails": {"duration": "PT1M"},
    }
    response = {"items": [item]}
    if next_page_token:
        response["nextPageToken"] = next_page_token
    return response


async def test_get_liked_videos_caches_first_page_under_empty_token(fake_redis, monkeypatch):
    fake_yt = MagicMock()
    fake_yt.videos.return_value.list.return_value.execute.return_value = _video_item(next_page_token="tokenA")
    monkeypatch.setattr(youtube, "_client", lambda credentials: fake_yt)

    result = await youtube.get_liked_videos(credentials=None, account_id="acc1")

    assert result["next_page_token"] == "tokenA"
    assert result["items"][0]["video_id"] == "dQw4w9WgXcQ"
    assert await fake_redis.get("liked:acc1:") is not None
    # Une page suivante distincte ne doit pas être confondue avec la première.
    assert await fake_redis.get("liked:acc1:tokenA") is None


async def test_rate_video_invalidates_every_cached_favorites_page_and_video_details(fake_redis, monkeypatch):
    await fake_redis.set("liked:acc1:", "stale-page-0")
    await fake_redis.set("liked:acc1:tokenA", "stale-page-1")
    await fake_redis.set("liked:acc2:", "vidéos likées d'un autre compte, ne doit pas bouger")
    await fake_redis.set("video_details:acc1:dQw4w9WgXcQ", "stale-details")

    fake_yt = MagicMock()
    monkeypatch.setattr(youtube, "_client", lambda credentials: fake_yt)

    await youtube.rate_video(credentials=None, account_id="acc1", video_id="dQw4w9WgXcQ", liked=True)

    assert await fake_redis.get("liked:acc1:") is None
    assert await fake_redis.get("liked:acc1:tokenA") is None
    assert await fake_redis.get("video_details:acc1:dQw4w9WgXcQ") is None
    # L'invalidation reste scopée au compte qui a liké/unliké.
    assert await fake_redis.get("liked:acc2:") is not None


async def test_add_playlist_item_invalidates_every_cached_playlist_items_page(fake_redis, monkeypatch):
    await fake_redis.set("playlist_items:acc1:PL123:", "stale-page-0")
    await fake_redis.set("playlist_items:acc1:PL123:tokenA", "stale-page-1")
    await fake_redis.set("playlists:acc1", "stale-playlists-list")

    fake_yt = MagicMock()
    fake_yt.playlistItems.return_value.insert.return_value.execute.return_value = {
        "id": "item1",
        "snippet": {"position": 0},
    }
    monkeypatch.setattr(youtube, "_client", lambda credentials: fake_yt)

    await youtube.add_playlist_item(
        credentials=None, account_id="acc1", playlist_id="PL123", video_id="dQw4w9WgXcQ"
    )

    assert await fake_redis.get("playlist_items:acc1:PL123:") is None
    assert await fake_redis.get("playlist_items:acc1:PL123:tokenA") is None
    assert await fake_redis.get("playlists:acc1") is None


async def test_remove_playlist_item_invalidates_every_cached_playlist_items_page(fake_redis, monkeypatch):
    await fake_redis.set("playlist_items:acc1:PL123:", "stale-page-0")
    await fake_redis.set("playlist_items:acc1:PL123:tokenA", "stale-page-1")
    await fake_redis.set("playlist_items:acc1:PL999:", "unrelated playlist, ne doit pas bouger")

    fake_yt = MagicMock()
    monkeypatch.setattr(youtube, "_client", lambda credentials: fake_yt)

    await youtube.remove_playlist_item(credentials=None, account_id="acc1", playlist_id="PL123", item_id="item1")

    assert await fake_redis.get("playlist_items:acc1:PL123:") is None
    assert await fake_redis.get("playlist_items:acc1:PL123:tokenA") is None
    assert await fake_redis.get("playlist_items:acc1:PL999:") == "unrelated playlist, ne doit pas bouger"


async def test_delete_playlist_invalidates_its_cached_items_pages(fake_redis, monkeypatch):
    await fake_redis.set("playlist_items:acc1:PL123:", "stale-page-0")
    await fake_redis.set("playlist_items:acc1:PL123:tokenA", "stale-page-1")
    await fake_redis.set("playlists:acc1", "stale-playlists-list")

    fake_yt = MagicMock()
    monkeypatch.setattr(youtube, "_client", lambda credentials: fake_yt)

    await youtube.delete_playlist(credentials=None, account_id="acc1", playlist_id="PL123")

    assert await fake_redis.get("playlist_items:acc1:PL123:") is None
    assert await fake_redis.get("playlist_items:acc1:PL123:tokenA") is None
    assert await fake_redis.get("playlists:acc1") is None
