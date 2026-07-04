# Contributing to OuyouyouTube

Thanks for your interest in the project! This document summarizes how to
set up a dev environment and submit a contribution.

## Before you start

This project was born out of strictly personal use (see the legal
disclaimer in [`README.md`](README.md#legal-disclaimer)). Contributions are
welcome as long as they stay within that spirit: a personal YouTube
client, not a content-distribution tool.

## Project principles

- **As little custom code as possible**: before writing code for a generic
  problem (`Range` requests, retries, caching, auth, scheduling...), check
  whether a standard library already handles it. This is the project's
  guiding principle — see the README.
- `yt-dlp` stays isolated in `server/app/downloader.py` — never called
  anywhere else in the code.
- No OAuth token should ever reach the client (cookie, localStorage,
  etc.) — credentials stay in Redis, the cookie only holds an opaque
  `session_id`.
- Videos must never persist beyond the configured TTL — any new feature
  touching storage must respect this principle.

## Dev setup

See the [Quick start](README.md#quick-start) section of the README to run
the backend (FastAPI + Redis) and the frontend (Vue + Vite) locally.

You'll need your own Google Cloud OAuth credentials (see the README) to
test the authentication flow end to end.

## Running the tests

```bash
# Backend
cd server && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v

# Frontend
cd front
npm run test
npm run build   # also checks that the production build passes
```

## Conventions

- **Branches**: `feat/<short-name>` for a feature, `fix/<short-name>` for a
  bug fix, `docs/<short-name>` for documentation.
- **Commits / PR titles**: follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `chore:`, ...), describing *why* rather than
  *what* (the diff already shows the what). Squash-merged PR titles become
  the commit message on `main`, so the PR title itself must follow this
  format — `release-please` (see below) reads it to compute the next
  version and changelog entry. `feat:` and `fix:` trigger a release;
  `feat!:`/a `BREAKING CHANGE:` footer trigger a major bump.
- **Roadmap**: [`ROADMAP.md`](ROADMAP.md) acts as memory between work
  sessions — check off items and document any important decision made
  along the way in a PR (known limitations, non-obvious implementation
  choices).
- **Releases**: automated by [`release-please`](https://github.com/googleapis/release-please)
  (`.github/workflows/release-please.yml`). Merges to `main` update a
  standing "release PR" that bumps the version and `CHANGELOG.md`;
  merging that PR cuts the actual GitHub Release and tag. No manual
  tagging needed.

## Submitting a PR

1. Fork the repo, create a branch off `main`.
2. Make your changes, keeping each PR focused on a single topic.
3. Verify tests and the build pass locally (see above) — GitHub Actions CI
   re-runs them on every PR anyway.
4. Open the PR describing *why* the change is needed and how you verified
   it (see the PR template).
5. Update `ROADMAP.md` if your PR closes an item on the list or adds a new
   one.

## Reporting a bug or requesting a feature

Use the GitHub issue templates. For a security vulnerability, follow
[`SECURITY.md`](SECURITY.md) instead — no public issue.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
