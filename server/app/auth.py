"""
OAuth2 Google — lib officielle google-auth-oauthlib, zéro custom crypto.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from app.cache import get_redis
from app.config import settings
from app.session import new_session_id, save_credentials, set_session_cookie

router = APIRouter(prefix="/auth", tags=["auth"])

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
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
async def login():
    flow = _flow()
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true")
    await get_redis().set(f"oauth_pkce:{state}", flow.code_verifier, ex=PKCE_TTL)
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

    session_id = new_session_id()
    await save_credentials(session_id, credentials)

    response = RedirectResponse(settings.frontend_origin)
    set_session_cookie(response, session_id)
    return response


@router.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(settings.frontend_origin)
    response.delete_cookie(settings.session_cookie_name)
    return response
