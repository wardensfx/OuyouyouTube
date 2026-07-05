from fastapi import APIRouter, Depends

from app import youtube
from app.session import Account, get_active_account

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/trending")
async def trending(page_token: str | None = None, account: Account = Depends(get_active_account)):
    return await youtube.get_trending(account.credentials, page_token=page_token)


@router.get("/subscriptions")
async def subscriptions_feed(account: Account = Depends(get_active_account)):
    return await youtube.get_subscriptions_feed(account.credentials, account.id)
