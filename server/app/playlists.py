from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app import youtube
from app.session import Account, get_active_account

router = APIRouter(tags=["playlists"])


class CreatePlaylistBody(BaseModel):
    title: str


class AddItemBody(BaseModel):
    video_id: str


@router.get("/playlists")
async def list_playlists(account: Account = Depends(get_active_account)):
    return await youtube.get_my_playlists(account.credentials, account.id)


@router.post("/playlists")
async def create_playlist(body: CreatePlaylistBody, account: Account = Depends(get_active_account)):
    return await youtube.create_playlist(account.credentials, account.id, body.title)


@router.get("/playlists/{playlist_id}/items")
async def playlist_items(playlist_id: str, account: Account = Depends(get_active_account)):
    return await youtube.get_playlist_items(account.credentials, playlist_id)


@router.post("/playlists/{playlist_id}/items")
async def add_playlist_item(playlist_id: str, body: AddItemBody, account: Account = Depends(get_active_account)):
    return await youtube.add_playlist_item(account.credentials, account.id, playlist_id, body.video_id)


@router.delete("/playlists/{playlist_id}/items/{item_id}")
async def remove_playlist_item(playlist_id: str, item_id: str, account: Account = Depends(get_active_account)):
    await youtube.remove_playlist_item(account.credentials, account.id, playlist_id, item_id)
    return {"ok": True}


@router.get("/favorites")
async def favorites(account: Account = Depends(get_active_account)):
    return await youtube.get_liked_videos(account.credentials, account.id)


@router.put("/favorites/{video_id}")
async def like_video(video_id: str, account: Account = Depends(get_active_account)):
    await youtube.rate_video(account.credentials, account.id, video_id, liked=True)
    return {"ok": True}


@router.delete("/favorites/{video_id}")
async def unlike_video(video_id: str, account: Account = Depends(get_active_account)):
    await youtube.rate_video(account.credentials, account.id, video_id, liked=False)
    return {"ok": True}
