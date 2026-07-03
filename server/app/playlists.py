from fastapi import APIRouter, Depends
from google.oauth2.credentials import Credentials

from app import youtube
from app.session import get_credentials

router = APIRouter(tags=["playlists"])


@router.get("/playlists")
async def list_playlists(credentials: Credentials = Depends(get_credentials)):
    return await youtube.get_my_playlists(credentials)


@router.get("/playlists/{playlist_id}/items")
async def playlist_items(playlist_id: str, credentials: Credentials = Depends(get_credentials)):
    return await youtube.get_playlist_items(credentials, playlist_id)


@router.get("/favorites")
async def favorites(credentials: Credentials = Depends(get_credentials)):
    return await youtube.get_liked_videos(credentials)
