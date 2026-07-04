from fastapi import APIRouter, Depends

from app import youtube
from app.session import Account, get_active_account

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/trending")
async def trending(account: Account = Depends(get_active_account)):
    return await youtube.get_trending(account.credentials)


@router.get("/subscriptions")
async def subscriptions_feed(account: Account = Depends(get_active_account)):
    return await youtube.get_subscriptions_feed(account.credentials, account.id)
