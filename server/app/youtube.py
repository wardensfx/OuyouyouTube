"""
Wrapper autour de YouTube Data API v3.
Toutes les données "sociales" (playlists, favoris, liked videos) passent
par ici, jamais par yt-dlp — yt-dlp ne sert qu'à récupérer le flux vidéo.
"""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.cache import get_json, set_json
from app.config import settings


def _client(credentials: Credentials):
    return build("youtube", "v3", credentials=credentials)


async def get_my_playlists(credentials: Credentials) -> list[dict]:
    cache_key = f"playlists:{credentials.client_id}:{_token_fingerprint(credentials)}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    playlists = []
    request = yt.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            playlists.append({
                "id": item["id"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
                "item_count": item["contentDetails"]["itemCount"],
            })
        request = yt.playlists().list_next(request, response)

    await set_json(cache_key, playlists, ttl=settings.metadata_ttl_seconds)
    return playlists


async def get_liked_videos(credentials: Credentials) -> list[dict]:
    """Favoris / vidéos likées de l'utilisateur."""
    cache_key = f"liked:{_token_fingerprint(credentials)}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    videos = []
    request = yt.videos().list(part="snippet,contentDetails", myRating="like", maxResults=50)
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            videos.append(_video_summary(item))
        request = yt.videos().list_next(request, response)

    await set_json(cache_key, videos, ttl=settings.metadata_ttl_seconds)
    return videos


async def get_playlist_items(credentials: Credentials, playlist_id: str) -> list[dict]:
    cache_key = f"playlist_items:{playlist_id}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    items = []
    request = yt.playlistItems().list(
        part="snippet,contentDetails", playlistId=playlist_id, maxResults=50
    )
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            items.append({
                "video_id": item["contentDetails"]["videoId"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
                "position": item["snippet"]["position"],
            })
        request = yt.playlistItems().list_next(request, response)

    await set_json(cache_key, items, ttl=settings.metadata_ttl_seconds)
    return items


def _video_summary(item: dict) -> dict:
    return {
        "video_id": item["id"],
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
        "duration": item["contentDetails"]["duration"],  # format ISO 8601
    }


def _token_fingerprint(credentials: Credentials) -> str:
    # simple hash non-sensible pour partitionner le cache par utilisateur
    return str(hash(credentials.token))[-10:]
