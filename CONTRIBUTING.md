# Contribuer à OuyouyouTube

Merci de l'intérêt porté au projet ! Ce document résume comment mettre en
place un environnement de dev et proposer une contribution.

## Avant de commencer

Ce projet est né d'un usage strictement personnel (voir l'avertissement
légal dans le [`README.md`](README.md#️-avertissement-légal)). Les
contributions sont bienvenues tant qu'elles restent dans cet esprit : un
client YouTube personnel, pas un outil de distribution de contenu.

## Principes du projet

- **Le moins de code custom possible** : avant d'écrire du code pour un
  problème générique (requêtes `Range`, retry, cache, auth, scheduling...),
  vérifie si une lib standard le fait déjà. C'est le principe directeur du
  projet, voir le README.
- `yt-dlp` reste isolé dans `server/app/downloader.py` — jamais appelé
  ailleurs dans le code.
- Aucun token OAuth ne doit jamais atterrir côté client (cookie,
  localStorage, etc.) — les credentials restent en Redis, le cookie ne
  contient qu'un `session_id` opaque.
- Les vidéos ne doivent jamais persister au-delà du TTL configuré — toute
  nouvelle fonctionnalité touchant au stockage doit respecter ce principe.

## Setup de développement

Voir la section [Démarrage rapide](README.md#démarrage-rapide) du README
pour lancer le backend (FastAPI + Redis) et le frontend (Vue + Vite) en
local.

Tu auras besoin de tes propres identifiants OAuth Google Cloud (voir le
README) pour tester le flow d'authentification de bout en bout.

## Lancer les tests

```bash
# Backend
cd server && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v

# Frontend
cd front
npm run test
npm run build   # vérifie aussi que le build de prod passe
```

## Conventions

- **Branches** : `feat/<nom-court>` pour une fonctionnalité, `fix/<nom-court>`
  pour un correctif, `docs/<nom-court>` pour de la documentation.
- **Commits** : message court à l'impératif décrivant le *pourquoi* plutôt
  que le *quoi* (le diff montre déjà le quoi).
- **Roadmap** : [`ROADMAP.md`](ROADMAP.md) sert de mémoire entre les
  sessions de travail — coche les cases et documente les décisions
  importantes prises au fil d'une PR (limites connues, choix
  d'implémentation non évidents).

## Proposer une PR

1. Fork le dépôt, crée une branche depuis `main`.
2. Fais tes changements, en gardant chaque PR focalisée sur un seul sujet.
3. Vérifie que les tests et le build passent en local (voir ci-dessus) — la
   CI GitHub Actions les relance de toute façon sur chaque PR.
4. Ouvre la PR en décrivant le *pourquoi* du changement et comment tu l'as
   vérifié (voir le template de PR).
5. Mets à jour `ROADMAP.md` si ta PR ferme un item de la liste ou en ajoute
   un nouveau.

## Signaler un bug ou proposer une fonctionnalité

Utilise les templates d'issue GitHub. Pour une vulnérabilité de sécurité,
suis plutôt [`SECURITY.md`](SECURITY.md) — pas d'issue publique.

## Code de conduite

Ce projet suit le [Contributor Covenant](CODE_OF_CONDUCT.md).
