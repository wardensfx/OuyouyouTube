# OuyouyouTube — PWA + backend yt-dlp

Client personnel YouTube : parcourt tes playlists/favoris via l'API officielle,
et streame la vidéo depuis ton propre serveur (yt-dlp télécharge, sert le fichier,
puis le supprime après un TTL). Aucune vidéo n'est stockée durablement.

## Structure

```
server/   FastAPI + yt-dlp + Redis (métadonnées + statut de download)
front/    Vue 3 + Vite + vite-plugin-pwa
```

## Lancer en dev

### Prérequis
- Python 3.11+
- Node 18+
- Redis (`redis-server`)
- Un projet Google Cloud avec l'API "YouTube Data API v3" activée
  et des identifiants OAuth 2.0 (type "Web application")

### Backend

```bash
cd server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # renseigner GOOGLE_CLIENT_ID / SECRET
redis-server &          # si pas déjà lancé
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd front
npm install
npm run dev
```

Ouvre http://localhost:5173 — le proxy Vite redirige `/auth`, `/playlists`,
`/favorites`, `/video/*` vers le backend sur le port 8000.

## Flow

1. `/auth/login` → OAuth Google → cookie de session (le token reste en Redis, jamais côté client)
2. `GET /playlists`, `/favorites` → wrap YouTube Data API, cache Redis 15 min
3. `POST /video/{id}/prepare` → lance yt-dlp en tâche de fond
4. `GET /video/{id}/status` → poll côté front jusqu'à `ready`
5. `GET /video/{id}/stream` → `FileResponse` (Range natif, seek OK)
6. Job périodique (`app/cleanup.py`) → supprime les fichiers > `VIDEO_TTL_SECONDS`

## Notes

- yt-dlp est importé comme lib Python, pas en subprocess — plus simple à maintenir.
- Le seek fonctionne nativement grâce à Starlette `FileResponse`, aucun code Range custom.
- Si YouTube throttle/bloque : exporter un `cookies.txt` (extension navigateur type
  "Get cookies.txt") et renseigner `YTDLP_COOKIES_FILE` dans `.env`.
