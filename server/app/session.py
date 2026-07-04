"""
Session côté serveur : le cookie ne contient qu'un session_id opaque.

Une session référence une liste de comptes Google liés (multi-comptes) et
lequel est actif. Chaque compte (credentials + profil) est stocké
indépendamment, keyé par account_id (l'id Google du compte), pour rester
simple : "lier un compte" == ajouter son id à la liste de la session.
"""
import json
import secrets
from dataclasses import dataclass

from fastapi import Request, Response, HTTPException
from google.oauth2.credentials import Credentials

from app.cache import get_redis
from app.config import settings

SESSION_TTL = 60 * 60 * 24 * 7  # 7 jours
ACCOUNT_TTL = 60 * 60 * 24 * 30  # 30 jours


def new_session_id() -> str:
    return secrets.token_urlsafe(32)


@dataclass
class Account:
    id: str
    email: str | None
    name: str | None
    picture: str | None
    credentials: Credentials


def _account_key(account_id: str) -> str:
    return f"account:{account_id}"


def _session_key(session_id: str) -> str:
    return f"session:{session_id}"


async def save_account(account_id: str, credentials: Credentials, profile: dict):
    payload = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "email": profile.get("email"),
        "name": profile.get("name"),
        "picture": profile.get("picture"),
    }
    await get_redis().set(_account_key(account_id), json.dumps(payload), ex=ACCOUNT_TTL)


async def _load_account(account_id: str) -> Account:
    raw = await get_redis().get(_account_key(account_id))
    if raw is None:
        raise HTTPException(status_code=401, detail="Compte introuvable, reconnecte-toi.")
    data = json.loads(raw)
    credentials = Credentials(
        token=data["token"],
        refresh_token=data["refresh_token"],
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=data["scopes"],
    )
    return Account(
        id=account_id,
        email=data.get("email"),
        name=data.get("name"),
        picture=data.get("picture"),
        credentials=credentials,
    )


async def _load_session(session_id: str) -> dict:
    raw = await get_redis().get(_session_key(session_id))
    if raw is None:
        raise HTTPException(status_code=401, detail="Session invalide, reconnecte-toi.")
    return json.loads(raw)


async def _save_session(session_id: str, data: dict):
    await get_redis().set(_session_key(session_id), json.dumps(data), ex=SESSION_TTL)


async def create_session(account_id: str) -> str:
    session_id = new_session_id()
    await _save_session(session_id, {"account_ids": [account_id], "active_account_id": account_id})
    return session_id


async def link_account(session_id: str, account_id: str):
    """Ajoute un compte à une session existante et le rend actif."""
    data = await _load_session(session_id)
    if account_id not in data["account_ids"]:
        data["account_ids"].append(account_id)
    data["active_account_id"] = account_id
    await _save_session(session_id, data)


async def list_accounts(session_id: str) -> list[Account]:
    data = await _load_session(session_id)
    return [await _load_account(aid) for aid in data["account_ids"]]


async def get_active_account_id(session_id: str) -> str:
    data = await _load_session(session_id)
    return data["active_account_id"]


async def activate_account(session_id: str, account_id: str):
    data = await _load_session(session_id)
    if account_id not in data["account_ids"]:
        raise HTTPException(status_code=404, detail="Ce compte n'est pas lié à cette session.")
    data["active_account_id"] = account_id
    await _save_session(session_id, data)


async def unlink_account(session_id: str, account_id: str):
    data = await _load_session(session_id)
    if account_id in data["account_ids"]:
        data["account_ids"].remove(account_id)
    if not data["account_ids"]:
        raise HTTPException(status_code=400, detail="Impossible de retirer le dernier compte lié.")
    if data["active_account_id"] == account_id:
        data["active_account_id"] = data["account_ids"][0]
    await _save_session(session_id, data)


def session_id_from_request(request: Request) -> str:
    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        raise HTTPException(status_code=401, detail="Non authentifié.")
    return session_id


async def get_active_account(request: Request) -> Account:
    session_id = session_id_from_request(request)
    account_id = await get_active_account_id(session_id)
    return await _load_account(account_id)


async def get_credentials(request: Request) -> Credentials:
    """Raccourci pour les routes qui n'ont besoin que des credentials du compte actif."""
    account = await get_active_account(request)
    return account.credentials


def set_session_cookie(response: Response, session_id: str):
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_TTL,
    )
