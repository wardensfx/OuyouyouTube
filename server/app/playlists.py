from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field

from app import youtube
from app.session import Account, get_active_account

router = APIRouter(tags=["playlists"])

VIDEO_ID_PATTERN = r"^[A-Za-z0-9_-]{11}$"


class CreatePlaylistBody(BaseModel):
    title: str


class AddItemBody(BaseModel):
    video_id: str = Field(pattern=VIDEO_ID_PATTERN)


class RenamePlaylistBody(BaseModel):
    title: str


@router.get("/playlists")
async def list_playlists(account: Account = Depends(get_active_account)):
    return await youtube.get_my_playlists(account.credentials, account.id)


@router.post("/playlists")
async def create_playlist(body: CreatePlaylistBody, account: Account = Depends(get_active_account)):
    return await youtube.create_playlist(account.credentials, account.id, body.title)


@router.patch("/playlists/{playlist_id}")
async def rename_playlist(playlist_id: str, body: RenamePlaylistBody, account: Account = Depends(get_active_account)):
    return await youtube.rename_playlist(account.credentials, account.id, playlist_id, body.title)


@router.delete("/playlists/{playlist_id}")
async def delete_playlist(playlist_id: str, account: Account = Depends(get_active_account)):
    await youtube.delete_playlist(account.credentials, account.id, playlist_id)
    return {"ok": True}


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
async def like_video(video_id: str = Path(pattern=VIDEO_ID_PATTERN), account: Account = Depends(get_active_account)):
    await youtube.rate_video(account.credentials, account.id, video_id, liked=True)
    return {"ok": True}


@router.delete("/favorites/{video_id}")
async def unlike_video(video_id: str = Path(pattern=VIDEO_ID_PATTERN), account: Account = Depends(get_active_account)):
    await youtube.rate_video(account.credentials, account.id, video_id, liked=False)
    return {"ok": True}
