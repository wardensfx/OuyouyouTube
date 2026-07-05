from fastapi import APIRouter, Depends, Query

from app import youtube
from app.session import Account, get_active_account

router = APIRouter(tags=["search"])


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    page_token: str | None = None,
    account: Account = Depends(get_active_account),
):
    return await youtube.search_videos(account.credentials, q, page_token=page_token)
