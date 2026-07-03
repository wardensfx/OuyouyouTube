"""
Session côté serveur : le cookie ne contient qu'un session_id opaque,
les credentials Google (access/refresh token) restent en Redis.
Évite de balader des tokens sensibles dans un cookie signé côté client.
"""
import json
import secrets

from fastapi import Request, Response, HTTPException
from google.oauth2.credentials import Credentials

from app.cache import get_redis
from app.config import settings

SESSION_TTL = 60 * 60 * 24 * 7  # 7 jours


def new_session_id() -> str:
    return secrets.token_urlsafe(32)


async def save_credentials(session_id: str, credentials: Credentials):
    payload = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    await get_redis().set(f"session:{session_id}", json.dumps(payload), ex=SESSION_TTL)


async def load_credentials(session_id: str) -> Credentials:
    raw = await get_redis().get(f"session:{session_id}")
    if raw is None:
        raise HTTPException(status_code=401, detail="Session invalide, reconnecte-toi.")
    data = json.loads(raw)
    return Credentials(**data)


async def get_credentials(request: Request) -> Credentials:
    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        raise HTTPException(status_code=401, detail="Non authentifié.")
    return await load_credentials(session_id)


def set_session_cookie(response: Response, session_id: str):
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_TTL,
    )
