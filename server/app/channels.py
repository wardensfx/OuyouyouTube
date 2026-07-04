from fastapi import APIRouter, Depends, HTTPException

from app import youtube
from app.session import Account, get_active_account

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("/{channel_id}")
async def channel_info(channel_id: str, account: Account = Depends(get_active_account)):
    info = await youtube.get_channel_info(account.credentials, channel_id)
    if info is None:
        raise HTTPException(status_code=404, detail="Chaîne introuvable.")
    return info


@router.get("/{channel_id}/videos")
async def channel_videos(channel_id: str, account: Account = Depends(get_active_account)):
    return await youtube.get_channel_videos(account.credentials, channel_id)
