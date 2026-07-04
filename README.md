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

Ouvre http://localhost:5173 — le proxy Vite redirige tout ce qui est sous
`/api/*` vers le backend sur le port 8000 (toutes les routes API vivent
sous ce préfixe, justement pour ne jamais entrer en collision avec les
routes du front, ex. `/search` ou `/playlists/manage`).

### Backend + Redis en container (recommandé, notamment sous Windows)

Redis n'a pas de build officiel Windows, et faire tourner le backend en
container évite d'avoir à gérer un venv Python à la main. `docker-compose.yml`
à la racine du repo lance Redis + backend, avec hot-reload :

```powershell
# Windows : Docker tourne dans une distro WSL (ex. Ubuntu)
wsl -d Ubuntu -- bash -c "cd /mnt/c/chemin/vers/OuyouyouTube && docker compose --profile dev up --watch"
```

```bash
# macOS/Linux avec Docker installé nativement
docker compose --profile dev up --watch
```

Le `--profile dev` est nécessaire : `backend` (dev) et `backend-prod` sont
deux services distincts profilés séparément, pour que le backend "dev"
(port 8000 publié, hot-reload) ne tourne jamais en même temps que le
profil `prod` (qui ne doit exposer que Caddy, voir plus bas).

`--watch` synchronise `server/app/` en live dans le container (les
changements de code déclenchent le reload d'uvicorn) et rebuild l'image
automatiquement si `requirements.txt` change. Le backend est exposé sur
`http://localhost:8000` comme en local classique.

Avant le premier lancement : `cp server/.env.example server/.env` et
renseigner `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.

### Frontend (toujours en direct, hors container)

```bash
cd front
npm install
npm run dev
```

### Backend en direct (sans Docker)

```bash
cd server
python3 -m venv .venv && source .venv/bin/activate   # Windows: python -m venv .venv puis .\.venv\Scripts\python.exe
pip install -r requirements.txt
cp .env.example .env   # renseigner GOOGLE_CLIENT_ID / SECRET
redis-server &          # ou le container Redis seul si pas de build natif (Windows)
uvicorn app.main:app --reload --port 8000
```

**Piège IPv4/IPv6 (Windows)** : sur certaines configs, `localhost` se résout
en priorité vers `::1` (IPv6). Si le backend n'écoute que sur `127.0.0.1`
(IPv4), le proxy Vite renvoie `502 Bad Gateway`. `front/vite.config.js`
pointe donc explicitement vers `http://127.0.0.1:8000` (pas `localhost`).

**OAuth en HTTP local** : `oauthlib` refuse par défaut l'échange de token
hors HTTPS. En dev, avec un `redirect_uri` en `http://localhost`, il faut
positionner `OAUTHLIB_INSECURE_TRANSPORT=1` dans l'environnement du backend
(déjà fait dans `docker-compose.yml` ; à définir toi-même si tu lances
uvicorn sans Docker). **Ne jamais faire ça en prod.**

**Scope OAuth élargi après coup** : `flow.authorization_url(..., include_granted_scopes="true")`
fait remonter, en plus des scopes demandés dans la requête en cours, tous
ceux déjà accordés à l'app par le passé (auth incrémentale Google — utile
pour ne pas re-demander le consentement à chaque élargissement de scope).
`oauthlib` traite par défaut tout écart avec ce qui a été demandé comme une
erreur, y compris un scope *en plus*. Nécessite `OAUTHLIB_RELAX_TOKEN_SCOPE=1`
dans l'environnement du backend (déjà fait dans `docker-compose.yml` et les
quadlets Podman) — contrairement à `OAUTHLIB_INSECURE_TRANSPORT`, celui-ci
est nécessaire aussi en prod, pas juste en dev.

## Déploiement (prod)

Le service `frontend` de `docker-compose.yml` (profil `prod`) build la SPA
et la sert via **Caddy** (`front/Dockerfile`, `front/Caddyfile`), qui fait
aussi office de reverse proxy vers le backend pour tout ce qui est sous
`/api/*`. Un seul point d'entrée, HTTPS automatique (Let's Encrypt) si
`SITE_ADDRESS` est un vrai nom de domaine — `backend-prod` (aussi profil
`prod`) ne publie aucun port sur l'hôte, seul `frontend` est joignable
depuis l'extérieur, comme dans les quadlets Podman.

```bash
cp .env.example .env   # définir SITE_ADDRESS
docker compose --profile prod up -d --build
```

Caddy écoute sur 8080 (HTTP) / 8443 (HTTPS), publiés tels quels sur l'hôte.

- `SITE_ADDRESS=:8080` (défaut) → HTTP simple, pratique pour tester en local
  sans domaine (pas de TLS).
- `SITE_ADDRESS=ouyouyoutube.mondomaine.fr` → Caddy obtient un certificat
  Let's Encrypt automatiquement sur 8443 (DNS doit pointer vers l'hôte ;
  redirige les ports externes 80/443 vers 8080/8443 sur cette machine si
  besoin, ex. sur la box/le routeur).

Dans tous les cas, `server/.env` (`GOOGLE_REDIRECT_URI`, `FRONTEND_ORIGIN`)
doit être cohérent avec `SITE_ADDRESS` — et le `redirect_uri` déclaré dans
Google Cloud Console doit correspondre exactement. Google refuse les
domaines `.local` (mDNS) : impossible de tester le login OAuth via
`http://xxx.local`, il faut un vrai domaine (ou `localhost`).

### Alternative : Podman Quadlet (derrière Traefik + pod_utils existants)

`services/*.container` fournit un équivalent du `docker-compose.yml` (profil
prod) sous forme d'unités systemd Quadlet, harmonisé avec les autres services
du même hôte (réseau `server_gateway`, pod `pod_utils`, style des labels
Traefik) : aucun port n'est publié par ces containers, ils rejoignent
`pod_utils` et sont rattachés à `server_gateway` comme les autres apps.
Le frontend est protégé par le middleware `authentik` en plus du login
Google ; `backend` et `redis` restent internes (pas de label Traefik).

⚠️ `pod_utils` partage le namespace réseau entre tous ses membres : vérifie
qu'aucun autre service du pod n'utilise déjà les ports 6379 (redis), 8000
(backend), 8080/8443 (frontend) avant d'activer ces units.

À adapter si besoin :
- `EnvironmentFile=%h/ouyouyoutube/server.env` (backend) → copier `server/.env`
  à cet endroit sur l'hôte.
- Le domaine (`ouyouyoutube.d-yann.fr`) dans `ouyouyoutube-frontend.container`
  si tu changes de nom.

```bash
podman build -t ouyouyoutube-backend:latest ./server
podman build -t ouyouyoutube-frontend:latest ./front

mkdir -p ~/.config/containers/systemd
cp services/*.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user enable --now ouyouyoutube-redis.service ouyouyoutube-backend.service ouyouyoutube-frontend.service
```

## Flow

1. `/api/auth/login` → OAuth Google → cookie de session (le token reste en Redis, jamais côté client)
2. `GET /api/playlists`, `/api/favorites` → wrap YouTube Data API, cache Redis 15 min
3. `POST /api/video/{id}/prepare` → lance yt-dlp en tâche de fond
4. `GET /api/video/{id}/status` → poll côté front jusqu'à `ready`
5. `GET /api/video/{id}/stream` → `FileResponse` (Range natif, seek OK)
6. Job périodique (`app/cleanup.py`) → supprime les fichiers > `VIDEO_TTL_SECONDS`

## Notes

- yt-dlp est importé comme lib Python, pas en subprocess — plus simple à maintenir.
- Le seek fonctionne nativement grâce à Starlette `FileResponse`, aucun code Range custom.
- Si YouTube throttle/bloque : exporter un `cookies.txt` (extension navigateur type
  "Get cookies.txt") et renseigner `YTDLP_COOKIES_FILE` dans `.env`.
