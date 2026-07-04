from fastapi import APIRouter, Depends

from app import youtube
from app.session import Account, get_active_account

router = APIRouter(tags=["playlists"])


@router.get("/playlists")
async def list_playlists(account: Account = Depends(get_active_account)):
    return await youtube.get_my_playlists(account.credentials, account.id)


@router.get("/playlists/{playlist_id}/items")
async def playlist_items(playlist_id: str, account: Account = Depends(get_active_account)):
    return await youtube.get_playlist_items(account.credentials, playlist_id)


@router.get("/favorites")
async def favorites(account: Account = Depends(get_active_account)):
    return await youtube.get_liked_videos(account.credentials, account.id)
