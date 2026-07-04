# Security Policy

## Signaler une vulnérabilité

Si tu découvres une faille de sécurité dans ce projet (par exemple :
contournement d'authentification, fuite de token OAuth, traversée de
répertoire, injection), merci de **ne pas** ouvrir une issue publique.

À la place :

- Ouvre un [security advisory GitHub](https://github.com/wardensfx/OuyouyouTube/security/advisories/new)
  (privé par défaut), ou
- Contacte le mainteneur directement via son profil GitHub.

Merci d'inclure autant de détails que possible : étapes de reproduction,
impact potentiel, et une suggestion de correctif si tu en as une.

## Ce qui est dans le périmètre

- Le backend FastAPI (`server/app/`) : auth OAuth2, gestion de session,
  routes API, téléchargement/streaming vidéo.
- Le frontend Vue (`front/src/`) : gestion des credentials côté client,
  appels API.

## Ce qui est explicitement hors périmètre

- Les failles de sécurité de yt-dlp lui-même, de la YouTube Data API, ou des
  dépendances tierces — remonte-les directement auprès de leurs mainteneurs
  respectifs (voir les liens dans le README).
- Le comportement d'une instance auto-hébergée mal configurée (identifiants
  OAuth exposés, `.env` commité, reverse proxy mal configuré) : voir le
  README pour les bonnes pratiques de déploiement.

## Bonnes pratiques déjà en place

Pour information, avant de signaler quelque chose, voici ce qui est déjà
vérifié/en place (voir aussi `ROADMAP.md`, section "Sécurité — revue et
correctifs") :

- Cookie de session `httponly`, `secure`, `samesite=lax` — le cookie ne
  contient qu'un `session_id` opaque, jamais un token.
- Tokens OAuth (access/refresh) stockés uniquement côté serveur (Redis),
  jamais transmis au client.
- Flow OAuth2 avec PKCE, `state` invalidé après usage.
- CORS restreint à l'origine du frontend (pas de wildcard).
- `video_id` validé (format fixe d'un ID YouTube) partout où il est accepté,
  pour empêcher toute traversée de répertoire via les routes vidéo.

## Limites connues (pas des vulnérabilités, mais bon à savoir)

- Pas de rate-limiting sur le déclenchement de téléchargement
  (`POST /video/{id}/prepare`) au-delà du garde-fou "un download à la fois
  par vidéo". Acceptable pour un usage personnel mono-utilisateur.
