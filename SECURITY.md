# Security Policy

## Reporting a vulnerability

If you find a security issue in this project (for example: authentication
bypass, OAuth token leak, directory traversal, injection), please **do
not** open a public issue.

Instead:

- Open a [GitHub security advisory](https://github.com/wardensfx/OuyouyouTube/security/advisories/new)
  (private by default), or
- Contact the maintainer directly through their GitHub profile.

Please include as much detail as possible: reproduction steps, potential
impact, and a suggested fix if you have one.

## What's in scope

- The FastAPI backend (`server/app/`): OAuth2 auth, session handling, API
  routes, video download/streaming.
- The Vue frontend (`front/src/`): client-side credential handling, API
  calls.

## What's explicitly out of scope

- Security issues in yt-dlp itself, the YouTube Data API, or third-party
  dependencies — report those directly to their respective maintainers
  (see the links in the README).
- The behavior of a misconfigured self-hosted instance (exposed OAuth
  credentials, a committed `.env`, a misconfigured reverse proxy): see the
  README for deployment best practices.

## Good practices already in place

For reference, before reporting something, here's what's already
verified/in place (see also the security-related notes in `ROADMAP.md`):

- Session cookie `httponly`, `secure`, `samesite=lax` — the cookie only
  holds an opaque `session_id`, never a token.
- OAuth tokens (access/refresh) stored server-side only (Redis), never
  sent to the client.
- OAuth2 flow with PKCE, `state` invalidated after use.
- CORS restricted to the frontend's origin (no wildcard).
- `video_id` validated (fixed YouTube ID format) everywhere it's accepted,
  to prevent directory traversal through the video routes.

## Known limitations (not vulnerabilities, but good to know)

- No rate-limiting on triggering a download (`POST /video/{id}/prepare`)
  beyond the "one download at a time per video" guard. Acceptable for a
  personal, single-user deployment.
