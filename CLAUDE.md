# OuyouyouTube — contexte projet

Client YouTube personnel : PWA qui reproduit le fonctionnement de l'app
originale (playlists, favoris, écran d'accueil) mais le visionnage est
streamé depuis un backend perso qui télécharge la vidéo via yt-dlp, la sert,
puis la supprime après un TTL. Aucun stockage durable de vidéo.

Usage strictement personnel, jamais distribué. Le risque légal identifié
(contournement des protections YouTube) est celui de yt-dlp lui-même,
accepté et assumé par l'utilisateur.

## Stack (décisions actées, ne pas dévier sans discussion)

- **Backend** : FastAPI (Python), choisi pour importer yt-dlp comme lib
  directement (`import yt_dlp`), pas de subprocess/parsing sauf pour ffmpeg
  si besoin de remux.
- **Streaming vidéo** : `FileResponse` de Starlette. Le support des `Range`
  headers (seek) est natif — ne jamais réimplémenter ça à la main.
- **Auth** : OAuth2 Google via `google-auth-oauthlib` (lib officielle).
  Session côté serveur : le cookie ne contient qu'un `session_id` opaque,
  les tokens Google restent en Redis (`app/session.py`). Ne jamais mettre
  de token dans un cookie côté client.
- **Données YouTube (playlists/favoris/métadonnées)** : YouTube Data API v3
  exclusivement. yt-dlp ne sert QUE à récupérer le flux vidéo, jamais les
  métadonnées sociales.
- **Cache métadonnées** : Redis, TTL 15 min (quota API limité).
- **Nettoyage fichiers vidéo** : APScheduler, job périodique dans
  `app/cleanup.py`, TTL configurable (`VIDEO_TTL_SECONDS`, 30 min par défaut).
- **Frontend** : Vue 3 + Vite + `vite-plugin-pwa`, Pinia pour le state,
  vue-router pour la navigation. Proxy dev vers `localhost:8000`.
- Principe général : **le moins de code custom possible**, on délègue aux
  libs standard à chaque fois que c'est possible (Range requests, OAuth,
  cache, scheduling).

## Structure

```
server/app/
  config.py      settings via pydantic-settings, lit .env
  session.py     session serveur (Redis), cookie = session_id only
  auth.py        routes OAuth (/auth/login, /callback, /logout)
  youtube.py     wrap YouTube Data API (playlists, favoris, items)
  cache.py       wrapper Redis async get/set JSON
  downloader.py  yt-dlp lib, état en Redis (downloading/ready/error)
  video.py       routes /video/{id}/prepare, /status, /stream
  playlists.py   routes /playlists, /playlists/{id}/items, /favorites
  cleanup.py     APScheduler, purge fichiers > TTL
  main.py        FastAPI app, CORS, lifespan (démarre le scheduler)

front/src/
  api/client.js       fetch wrapper, credentials: 'include' obligatoire
  stores/library.js   Pinia store (playlists + favoris)
  router/index.js     routes: /, /playlist/:id, /watch/:videoId
  views/
    Home.vue           grille playlists + favoris
    PlaylistDetail.vue  items d'une playlist
    Player.vue          prepare → poll status → <video> une fois ready
  components/
    VideoCard.vue, PlaylistCard.vue
```

## État actuel

Squelette fonctionnel bout en bout, **non testé avec de vrais identifiants
Google** (pas de compte OAuth configuré côté sandbox où le code a été écrit).

Vérifié :
- Backend s'importe sans erreur, 10 routes montées et confirmées via
  OpenAPI schema (`/auth/login`, `/auth/callback`, `/auth/logout`,
  `/playlists`, `/playlists/{id}/items`, `/favorites`,
  `/video/{id}/prepare`, `/video/{id}/status`, `/video/{id}/stream`,
  `/health`).
- Frontend : `npm run build` passe, PWA générée (manifest + service worker).

Pas vérifié / pas fait :
- Flow OAuth complet de bout en bout (jamais lancé avec de vrais identifiants).
- Téléchargement yt-dlp réel jamais exécuté (pas testé avec une vraie vidéo).
- Aucun test automatisé (unit/e2e) écrit.
- Icônes PWA (`front/public/icons/icon-192.png`, `icon-512.png`) : référencées
  dans `vite.config.js` mais **les fichiers n'existent pas encore**, il faut
  les générer/fournir.
- Pas de gestion d'erreur fine côté yt-dlp (vidéo privée, région bloquée,
  age-restricted, etc.) — actuellement juste catché en `STATUS_ERROR` générique.
- Pas de gestion du refresh token expiré / révoqué côté `session.py`
  (`Credentials` reconstruit sans vérifier l'expiration avant usage).
- Pas de reverse proxy / déploiement (Caddy mentionné en discussion mais
  rien de configuré).
- `YTDLP_COOKIES_FILE` prévu dans la config mais pas de doc sur comment
  l'exporter proprement ni de fallback si absent.

## Prochaines étapes (par ordre de priorité suggéré)

1. Configurer un projet Google Cloud + identifiants OAuth, remplir `.env`,
   tester le flow `/auth/login` → `/auth/callback` de bout en bout.
2. Lancer Redis, tester `/playlists` et `/favorites` avec un vrai compte.
3. Tester `/video/{id}/prepare` avec une vraie vidéo YouTube, vérifier que
   le fichier apparaît dans `CACHE_DIR`, que `/stream` sert bien avec Range
   (tester le seek dans le `<video>` du front).
4. Générer les icônes PWA manquantes.
5. Améliorer la gestion d'erreurs downloader (messages différenciés selon
   le type d'échec yt-dlp).
6. Tester l'installation PWA sur mobile réel (Add to Home Screen), vérifier
   le comportement du service worker (surtout `navigateFallbackDenylist`
   pour ne jamais cacher les routes `/video/*`).

## Contraintes à respecter en continuant le travail

- Garder l'archi "peu de custom" : avant d'écrire du code pour un problème
  (range requests, retry, cache, queue...), vérifier si une lib standard
  le fait déjà.
- Ne jamais stocker de token OAuth côté client (cookie, localStorage, etc.).
- Les vidéos ne doivent jamais persister au-delà du TTL — toute nouvelle
  fonctionnalité touchant au stockage doit respecter ce principe.
- yt-dlp reste isolé dans `downloader.py` — pas d'appel yt-dlp ailleurs
  dans le code.
