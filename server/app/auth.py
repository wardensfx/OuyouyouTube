"""
OAuth2 Google — lib officielle google-auth-oauthlib, zéro custom crypto.
"""
import base64

import requests
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.cache import get_redis
from app.config import settings
from app.session import (
    activate_account,
    create_session,
    get_active_account_id,
    link_account,
    list_accounts,
    save_account,
    session_id_from_request,
    set_session_cookie,
    unlink_account,
)

AVATAR_TTL = 60 * 60 * 2  # 2h — évite de re-taper le CDN Google (rate-limite/429)

router = APIRouter(prefix="/auth", tags=["auth"])

# "youtube" (gestion complète) remplace "youtube.readonly" : nécessaire pour
# ajouter/retirer des vidéos aux playlists et favoris depuis l'app.
# "userinfo.profile" donne nom + avatar, utilisés par le sélecteur de compte.
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# PKCE : le code_verifier vit sur l'instance Flow qui génère l'URL d'autorisation.
# Comme /login et /callback sont deux requêtes (et deux instances Flow) distinctes,
# il faut le faire transiter par un stockage partagé, keyé par `state`.
PKCE_TTL = 600


def _flow(code_verifier: str | None = None) -> Flow:
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
        code_verifier=code_verifier,
    )


@router.get("/login")
async def login(request: Request, link: bool = False):
    """`?link=true` : lie un compte supplémentaire à la session existante
    au lieu d'en créer une nouvelle (sélecteur multi-comptes)."""
    flow = _flow()
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true")
    await get_redis().set(f"oauth_pkce:{state}", flow.code_verifier, ex=PKCE_TTL)

    if link:
        session_id = request.cookies.get(settings.session_cookie_name)
        if session_id:
            await get_redis().set(f"oauth_link:{state}", session_id, ex=PKCE_TTL)

    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(request: Request):
    state = request.query_params.get("state")
    code_verifier = await get_redis().getdel(f"oauth_pkce:{state}") if state else None
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Session OAuth expirée ou invalide, reconnecte-toi.")

    flow = _flow(code_verifier=code_verifier)
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    profile = build("oauth2", "v2", credentials=credentials).userinfo().get().execute()
    account_id = profile["id"]
    await save_account(account_id, credentials, profile)

    link_session_id = await get_redis().getdel(f"oauth_link:{state}")
    if link_session_id:
        await link_account(link_session_id, account_id)
        session_id = link_session_id
    else:
        session_id = await create_session(account_id)

    response = RedirectResponse(settings.frontend_origin)
    set_session_cookie(response, session_id)
    return response


@router.get("/accounts")
async def accounts(request: Request):
    session_id = session_id_from_request(request)
    active_id = await get_active_account_id(session_id)
    return [
        {"id": a.id, "email": a.email, "name": a.name, "picture": a.picture, "active": a.id == active_id}
        for a in await list_accounts(session_id)
    ]


@router.post("/accounts/{account_id}/activate")
async def activate(account_id: str, request: Request):
    session_id = session_id_from_request(request)
    await activate_account(session_id, account_id)
    return {"active_account_id": account_id}


@router.delete("/accounts/{account_id}")
async def unlink(account_id: str, request: Request):
    session_id = session_id_from_request(request)
    await unlink_account(session_id, account_id)
    return {"ok": True}


@router.get("/accounts/{account_id}/avatar")
async def avatar(account_id: str, request: Request):
    """Proxy + cache la photo de profil Google (sinon le CDN nous 429 à force
    de la re-demander à chaque reload)."""
    session_id = session_id_from_request(request)
    accounts_list = await list_accounts(session_id)
    account = next((a for a in accounts_list if a.id == account_id), None)
    if account is None:
        raise HTTPException(status_code=404, detail="Compte introuvable.")

    cache_key = f"avatar:{account_id}"
    cached = await get_redis().get(cache_key)
    if cached is None:
        if not account.picture:
            raise HTTPException(status_code=404, detail="Pas de photo de profil.")
        upstream = requests.get(account.picture, timeout=5)
        upstream.raise_for_status()
        content_type = upstream.headers.get("content-type", "image/jpeg")
        cached = f"{content_type}|{base64.b64encode(upstream.content).decode()}"
        await get_redis().set(cache_key, cached, ex=AVATAR_TTL)

    content_type, encoded = cached.split("|", 1)
    return Response(
        content=base64.b64decode(encoded),
        media_type=content_type,
        headers={"Cache-Control": f"public, max-age={AVATAR_TTL}"},
    )


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Pas de RedirectResponse ici : appelé via fetch() depuis le front, qui
    gère lui-même la navigation. Un redirect 307 sur un POST ferait suivre au
    navigateur un second POST vers la cible (méthode préservée), que Caddy
    rejette en 405 côté fichiers statiques."""
    response.delete_cookie(settings.session_cookie_name)
    return {"ok": True}
