# OuyouyouTube — project context

Personal YouTube client: a PWA that reproduces the official app's behavior
(playlists, favorites, subscriptions, search, home feed) but playback is
streamed from a personal backend that downloads the video via yt-dlp,
serves it, then deletes it after a TTL. No durable video storage.

Intended for strictly personal use (one deployed instance = one personal
use). The repo's source code is public (MIT license, see `README.md`),
but that doesn't change the tool's purpose: everyone hosts their own
instance for their own YouTube account, this isn't a shared public
service. The identified legal risk (circumventing YouTube's protections)
is yt-dlp's own risk, accepted and assumed by each instance's user — see
the legal disclaimer in `README.md`.

## Stack (settled decisions, don't deviate without discussion)

- **Backend**: FastAPI (Python), chosen so `yt_dlp` can be imported
  directly as a lib (`import yt_dlp`), no subprocess/parsing except for
  ffmpeg if remuxing is needed.
- **Video streaming**: Starlette's `FileResponse`. `Range` header support
  (seek) is native — never hand-roll this.
- **Auth**: Google OAuth2 via `google-auth-oauthlib` (official lib), with
  PKCE. Server-side session: the cookie only holds an opaque `session_id`,
  Google tokens stay in Redis (`app/session.py`). Never put a token in a
  client-side cookie. Supports multiple linked Google accounts per
  session (account switcher).
- **YouTube data (playlists/favorites/metadata)**: YouTube Data API v3
  exclusively. yt-dlp is used ONLY to fetch the video stream, never social
  metadata.
- **Metadata cache**: Redis, 15 min TTL (limited API quota).
- **Video file cleanup**: APScheduler, periodic job in `app/cleanup.py`,
  configurable TTL (`VIDEO_TTL_SECONDS`, 30 min by default).
- **Frontend**: Vue 3 + Vite + `vite-plugin-pwa`, Pinia for state,
  vue-router for navigation. Dev proxy to `localhost:8000`.
- General principle: **as little custom code as possible** — delegate to
  standard libs whenever possible (Range requests, OAuth, cache,
  scheduling).

## Structure

```
server/app/
  config.py      settings via pydantic-settings, reads .env
  session.py     server-side session (Redis), cookie = session_id only,
                 supports multiple linked accounts per session
  auth.py        OAuth routes (/api/auth/login, /callback, /logout,
                 /accounts, account switcher, avatar proxy)
  youtube.py     wraps the YouTube Data API (playlists, favorites, items,
                 search, trending, subscriptions feed, channels)
  cache.py       async Redis get/set JSON wrapper
  downloader.py  yt-dlp lib, state in Redis (downloading/ready/error)
  video.py       routes /api/video/{id}/prepare, /status, /stream, /info,
                 /progress, /watched
  playlists.py   routes /api/playlists, /api/playlists/{id}/items,
                 /api/favorites
  search.py      route /api/search
  home.py        routes /api/home/trending, /api/home/subscriptions
  progress.py    watch progress / watched status, per account/video
  cleanup.py     APScheduler, purges files > TTL
  main.py        FastAPI app, CORS, lifespan (starts the scheduler); all
                 routers mounted under /api to avoid colliding with
                 frontend routes

front/src/
  api/client.js       fetch wrapper, credentials: 'include' required, all
                       calls under /api
  stores/             Pinia stores: library.js (playlists + favorites),
                       playlistOrder.js, progress.js, toast.js
  router/index.js      routes: /, /playlist/:id, /playlists/manage,
                       /favorites, /subscriptions, /trending,
                       /watch/:videoId, /search
  views/
    Home.vue           customizable home feed (subscriptions, trending,
                       playlists, favorites sections)
    PlaylistDetail.vue  items of a playlist
    ManagePlaylists.vue reorder/rename/delete playlists
    Player.vue          prepare → poll status → <video> once ready,
                       YouTube-style keyboard shortcuts
    Search.vue, Trending.vue, Subscriptions.vue, Liked.vue
  components/
    VideoCard.vue, PlaylistCard.vue, AccountSwitcher.vue, Sidebar.vue,
    BottomNav.vue, AddToPlaylistModal.vue, ToastContainer.vue,
    ScrollToTop.vue
```

## Current state

The project has grown well past the initial skeleton — see `ROADMAP.md`
for the full, up-to-date list of what's implemented (most of the Must/
Should/Could items are done), known constraints, and past fixes. Don't
duplicate that tracking here; treat `ROADMAP.md` as the source of truth
for feature status.

Automated tests exist (`server/tests/` with pytest, `front/src/utils/*.test.js`
with vitest) and run in CI (`.github/workflows/ci.yml`) on every push/PR.

## Constraints to respect going forward

- Keep the "as little custom as possible" architecture: before writing
  code for a problem (range requests, retry, cache, queue...), check
  whether a standard lib already does it.
- Never store an OAuth token client-side (cookie, localStorage, etc.).
- Videos must never persist beyond the TTL — any new feature touching
  storage must respect this.
- yt-dlp stays isolated in `downloader.py` — no yt-dlp calls anywhere
  else in the code.
- `video_id` must stay validated (fixed YouTube ID format) wherever it's
  accepted, since it flows into a filesystem path and a URL passed to
  yt-dlp.
