"""
Wrapper autour de YouTube Data API v3.
Toutes les données "sociales" (playlists, favoris, liked videos) passent
par ici, jamais par yt-dlp — yt-dlp ne sert qu'à récupérer le flux vidéo.
"""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.cache import delete_prefix, get_json, get_redis, set_json
from app.config import settings

# Taille de page pour les listes potentiellement non bornées (favoris,
# tendances, vidéos de chaîne, recherche) — cf. issue #78. Les autres listes
# (playlists de l'utilisateur, items d'une playlist) restent chargées en
# entier : elles alimentent le réordonnancement/tri côté client sur
# l'ensemble complet, qui casserait avec une pagination partielle.
PAGE_SIZE = 24


def _client(credentials: Credentials):
    return build("youtube", "v3", credentials=credentials)


def _page_kwargs(page_token: str | None) -> dict:
    return {"pageToken": page_token} if page_token else {}


def _bulk_durations(yt, video_ids: list[str]) -> dict[str, str]:
    """videos.list accepte jusqu'à 50 ids séparés par des virgules par appel :
    un seul appel groupé (par tranche de 50) suffit pour récupérer la durée
    de toute une page de playlist/abonnements, plutôt qu'un appel par vidéo.
    Nécessaire car playlistItems.list et activities.list n'exposent que le
    contentDetails de l'ITEM (videoId, date), jamais celui de la vidéo elle-même."""
    durations = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        response = yt.videos().list(part="contentDetails", id=",".join(chunk)).execute()
        for item in response.get("items", []):
            durations[item["id"]] = item["contentDetails"]["duration"]
    return durations


async def get_my_playlists(credentials: Credentials, account_id: str) -> list[dict]:
    cache_key = f"playlists:{account_id}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    playlists = []
    request = yt.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            playlists.append({
                "id": item["id"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
                "item_count": item["contentDetails"]["itemCount"],
            })
        request = yt.playlists().list_next(request, response)

    await set_json(cache_key, playlists, ttl=settings.metadata_ttl_seconds)
    return playlists


async def get_liked_videos(credentials: Credentials, account_id: str, page_token: str | None = None) -> dict:
    """Favoris / vidéos likées de l'utilisateur, une page à la fois."""
    cache_key = f"liked:{account_id}:{page_token or ''}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    response = yt.videos().list(
        part="snippet,contentDetails", myRating="like", maxResults=PAGE_SIZE, **_page_kwargs(page_token)
    ).execute()
    result = {
        "items": [_video_summary(item) for item in response.get("items", [])],
        "next_page_token": response.get("nextPageToken"),
    }

    await set_json(cache_key, result, ttl=settings.metadata_ttl_seconds)
    return result


async def get_playlist_items(
    credentials: Credentials, account_id: str, playlist_id: str, page_token: str | None = None
) -> dict:
    """Une page à la fois (cf. issue #78) : une playlist peut contenir des
    milliers de vidéos. Le tri/filtre plein-ensemble de PlaylistDetail.vue
    déclenche côté frontend le chargement de toutes les pages restantes
    avant d'opérer — cette fonction elle-même reste simplement paginée.

    Clé de cache namespacée par account_id (cf. issue #82) : une playlist
    peut être privée, donc réservée au compte qui l'a demandée — sans ça,
    un second compte lié à la même session la recevrait depuis le cache
    sans jamais repasser par la vérification de permission de Google."""
    cache_key = f"playlist_items:{account_id}:{playlist_id}:{page_token or ''}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    response = yt.playlistItems().list(
        part="snippet,contentDetails", playlistId=playlist_id, maxResults=PAGE_SIZE, **_page_kwargs(page_token)
    ).execute()
    items = [
        {
            "item_id": item["id"],
            "video_id": item["contentDetails"]["videoId"],
            "title": item["snippet"]["title"],
            # videoOwnerChannelTitle = chaîne de la vidéo ; channelTitle
            # (snippet) serait la chaîne propriétaire de la PLAYLIST.
            "channel": item["snippet"].get("videoOwnerChannelTitle"),
            "channel_id": item["snippet"].get("videoOwnerChannelId"),
            "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
            "position": item["snippet"]["position"],
            "published_at": item["contentDetails"].get("videoPublishedAt"),
        }
        for item in response.get("items", [])
    ]

    durations = _bulk_durations(yt, [i["video_id"] for i in items])
    for i in items:
        i["duration"] = durations.get(i["video_id"])

    result = {"items": items, "next_page_token": response.get("nextPageToken")}
    await set_json(cache_key, result, ttl=settings.metadata_ttl_seconds)
    return result


def _video_summary(item: dict) -> dict:
    thumbnails = item["snippet"]["thumbnails"]
    return {
        "video_id": item["id"],
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "channel_id": item["snippet"]["channelId"],
        "thumbnail": thumbnails.get("medium", {}).get("url"),
        # Petit format (120x90) en plus du "medium" (320x180) : certaines
        # plateformes (MediaSession sur iOS) ne rendent fiablement qu'une
        # artwork sous ~128x128, cf. issue #74.
        "thumbnail_small": thumbnails.get("default", {}).get("url"),
        "duration": item["contentDetails"]["duration"],  # format ISO 8601
        "published_at": item["snippet"]["publishedAt"],
    }


async def search_videos(credentials: Credentials, query: str, page_token: str | None = None) -> dict:
    """search.list ne renvoie que id/snippet (jamais contentDetails, même en
    le demandant) — la durée nécessite un second appel groupé sur videos.list.
    Une page à la fois (cf. issue #78) : auparavant plafonné à 25 résultats
    sans moyen d'aller plus loin, on répercute maintenant le pageToken."""
    cache_key = f"search:{query.lower()}:{page_token or ''}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    response = yt.search().list(
        part="snippet", q=query, type="video", maxResults=PAGE_SIZE, **_page_kwargs(page_token)
    ).execute()
    results = [
        {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "channel_id": item["snippet"]["channelId"],
            "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
            "published_at": item["snippet"]["publishedAt"],
        }
        for item in response.get("items", [])
    ]
    durations = _bulk_durations(yt, [r["video_id"] for r in results])
    for r in results:
        r["duration"] = durations.get(r["video_id"])

    result = {"items": results, "next_page_token": response.get("nextPageToken")}
    await set_json(cache_key, result, ttl=settings.metadata_ttl_seconds)
    return result


async def get_video_details(credentials: Credentials, account_id: str, video_id: str) -> dict:
    """Métadonnées d'une seule vidéo, pour l'affichage sous le lecteur.

    Clé de cache namespacée par account_id (cf. issue #82) : une vidéo peut
    être privée (réservée à son propriétaire), donc réservée au compte qui
    l'a demandée — sans ça, un second compte lié à la même session la
    recevrait depuis le cache sans jamais repasser par la vérification de
    permission de Google."""
    cache_key = f"video_details:{account_id}:{video_id}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    response = yt.videos().list(part="snippet,contentDetails,statistics", id=video_id).execute()
    items = response.get("items", [])
    if not items:
        return None

    item = items[0]
    # `videos.getRating` est le seul moyen de connaître l'avis de l'utilisateur
    # sur CETTE vidéo précise (1 unité de quota) — dériver "aimée" d'une
    # recherche dans la liste des favoris ne marche plus de façon fiable
    # depuis que celle-ci est paginée (#78) : une vidéo aimée mais absente des
    # pages déjà chargées apparaissait à tort comme non aimée (#87).
    rating_response = yt.videos().getRating(id=video_id).execute()
    rating_items = rating_response.get("items", [])
    liked = bool(rating_items) and rating_items[0].get("rating") == "like"

    details = {
        **_video_summary(item),
        "description": item["snippet"].get("description", ""),
        "view_count": item.get("statistics", {}).get("viewCount"),
        "liked": liked,
    }
    await set_json(cache_key, details, ttl=settings.metadata_ttl_seconds)
    return details


# Bornes pour l'agrégation "abonnements" : un appel activities.list par
# chaîne suivie (1 unité chacun) — on plafonne pour rester raisonnable en
# quota/latence sur un compte avec beaucoup d'abonnements.
SUBSCRIPTIONS_CHANNEL_CAP = 15
SUBSCRIPTIONS_PER_CHANNEL = 5


async def get_trending(credentials: Credentials, region: str = "FR", page_token: str | None = None) -> dict:
    """Pas de notion de compte ici (mêmes tendances pour tout le monde dans
    une région) — le cache n'a donc pas besoin d'être partitionné par compte.
    Une page à la fois (cf. issue #78) plutôt que d'accumuler tout le
    plafond de ~200 vidéos de YouTube d'un coup."""
    cache_key = f"trending:{region}:{page_token or ''}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    response = yt.videos().list(
        part="snippet,contentDetails",
        chart="mostPopular",
        regionCode=region,
        maxResults=PAGE_SIZE,
        **_page_kwargs(page_token),
    ).execute()
    result = {
        "items": [_video_summary(item) for item in response.get("items", [])],
        "next_page_token": response.get("nextPageToken"),
    }

    await set_json(cache_key, result, ttl=settings.metadata_ttl_seconds)
    return result


async def get_subscriptions_feed(credentials: Credentials, account_id: str) -> list[dict]:
    """Pas d'équivalent officiel à `activities.list(home=true)` (déprécié) :
    on reconstruit un flux en interrogeant les dernières activités de chaque
    chaîne suivie, plafonné à SUBSCRIPTIONS_CHANNEL_CAP chaînes."""
    cache_key = f"subscriptions_feed:{account_id}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    channel_ids = []
    request = yt.subscriptions().list(part="snippet", mine=True, maxResults=50, order="alphabetical")
    while request is not None and len(channel_ids) < SUBSCRIPTIONS_CHANNEL_CAP:
        response = request.execute()
        for item in response.get("items", []):
            channel_ids.append(item["snippet"]["resourceId"]["channelId"])
        request = yt.subscriptions().list_next(request, response)
    channel_ids = channel_ids[:SUBSCRIPTIONS_CHANNEL_CAP]

    videos = []
    for channel_id in channel_ids:
        response = yt.activities().list(
            part="snippet,contentDetails", channelId=channel_id, maxResults=SUBSCRIPTIONS_PER_CHANNEL
        ).execute()
        for item in response.get("items", []):
            upload = item.get("contentDetails", {}).get("upload")
            if not upload:
                continue  # on ignore les autres types d'activité (likes, playlists créées, etc.)
            videos.append({
                "video_id": upload["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "channel_id": item["snippet"]["channelId"],
                "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
                "published_at": item["snippet"]["publishedAt"],
            })

    durations = _bulk_durations(yt, [v["video_id"] for v in videos])
    for v in videos:
        v["duration"] = durations.get(v["video_id"])

    videos.sort(key=lambda v: v["published_at"], reverse=True)
    await set_json(cache_key, videos, ttl=settings.metadata_ttl_seconds)
    return videos


async def create_playlist(credentials: Credentials, account_id: str, title: str) -> dict:
    yt = _client(credentials)
    response = yt.playlists().insert(part="snippet", body={"snippet": {"title": title}}).execute()
    await get_redis().delete(f"playlists:{account_id}")
    return {"id": response["id"], "title": response["snippet"]["title"], "thumbnail": None, "item_count": 0}


async def rename_playlist(credentials: Credentials, account_id: str, playlist_id: str, title: str) -> dict:
    """playlists.update n'est pas un vrai PATCH : il faut renvoyer le
    snippet complet, sinon les champs non fournis (description, tags…)
    seraient réinitialisés."""
    yt = _client(credentials)
    current = yt.playlists().list(part="snippet", id=playlist_id).execute()
    items = current.get("items", [])
    if not items:
        raise ValueError("Playlist introuvable")
    snippet = items[0]["snippet"]
    snippet["title"] = title
    response = yt.playlists().update(part="snippet", body={"id": playlist_id, "snippet": snippet}).execute()
    await get_redis().delete(f"playlists:{account_id}")
    return {"id": response["id"], "title": response["snippet"]["title"]}


async def delete_playlist(credentials: Credentials, account_id: str, playlist_id: str):
    yt = _client(credentials)
    yt.playlists().delete(id=playlist_id).execute()
    await get_redis().delete(f"playlists:{account_id}")
    await delete_prefix(f"playlist_items:{account_id}:{playlist_id}:")


async def add_playlist_item(credentials: Credentials, account_id: str, playlist_id: str, video_id: str) -> dict:
    yt = _client(credentials)
    response = yt.playlistItems().insert(
        part="snippet",
        body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
    ).execute()
    await delete_prefix(f"playlist_items:{account_id}:{playlist_id}:")
    await get_redis().delete(f"playlists:{account_id}")
    return {"item_id": response["id"], "video_id": video_id, "position": response["snippet"]["position"]}


async def remove_playlist_item(credentials: Credentials, account_id: str, playlist_id: str, item_id: str):
    yt = _client(credentials)
    yt.playlistItems().delete(id=item_id).execute()
    await delete_prefix(f"playlist_items:{account_id}:{playlist_id}:")
    await get_redis().delete(f"playlists:{account_id}")


async def rate_video(credentials: Credentials, account_id: str, video_id: str, liked: bool):
    yt = _client(credentials)
    yt.videos().rate(id=video_id, rating="like" if liked else "none").execute()
    await delete_prefix(f"liked:{account_id}:")
    await get_redis().delete(f"video_details:{account_id}:{video_id}")


async def get_channel_info(credentials: Credentials, channel_id: str) -> dict | None:
    cache_key = f"channel:{channel_id}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    response = yt.channels().list(part="snippet,statistics", id=channel_id).execute()
    items = response.get("items", [])
    if not items:
        return None

    item = items[0]
    stats = item.get("statistics", {})
    info = {
        "channel_id": item["id"],
        "title": item["snippet"]["title"],
        "description": item["snippet"].get("description", ""),
        "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
        "subscriber_count": None if stats.get("hiddenSubscriberCount") else stats.get("subscriberCount"),
        "video_count": stats.get("videoCount"),
    }
    await set_json(cache_key, info, ttl=settings.metadata_ttl_seconds)
    return info


async def _get_uploads_playlist_id(yt, channel_id: str) -> str | None:
    """L'ID de la playlist "uploads" d'une chaîne ne change jamais : mis en
    cache indépendamment des pages de vidéos plutôt que refetché à chaque
    page (cf. get_channel_videos)."""
    cache_key = f"channel_uploads_playlist:{channel_id}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached or None

    response = yt.channels().list(part="contentDetails", id=channel_id).execute()
    items = response.get("items", [])
    playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"] if items else ""
    await set_json(cache_key, playlist_id, ttl=settings.metadata_ttl_seconds)
    return playlist_id or None


async def get_channel_videos(credentials: Credentials, channel_id: str, page_token: str | None = None) -> dict:
    """Passe par la playlist "uploads" de la chaîne (1 unité) plutôt que
    search.list (100 unités) — même logique d'économie de quota que pour
    les abonnements (cf. get_subscriptions_feed). Une page à la fois (cf.
    issue #78) : une grosse chaîne peut avoir des milliers de vidéos."""
    cache_key = f"channel_videos:{channel_id}:{page_token or ''}"
    cached = await get_json(cache_key)
    if cached is not None:
        return cached

    yt = _client(credentials)
    uploads_playlist_id = await _get_uploads_playlist_id(yt, channel_id)
    if uploads_playlist_id is None:
        return {"items": [], "next_page_token": None}

    response = yt.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=PAGE_SIZE,
        **_page_kwargs(page_token),
    ).execute()
    videos = [
        {
            "video_id": item["contentDetails"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"].get("channelTitle"),
            "channel_id": channel_id,
            "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url"),
            "published_at": item["contentDetails"].get("videoPublishedAt"),
        }
        for item in response.get("items", [])
    ]
    durations = _bulk_durations(yt, [v["video_id"] for v in videos])
    for v in videos:
        v["duration"] = durations.get(v["video_id"])

    result = {"items": videos, "next_page_token": response.get("nextPageToken")}
    await set_json(cache_key, result, ttl=settings.metadata_ttl_seconds)
    return result
