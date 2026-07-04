# Roadmap

Suivi des fonctionnalités du clone, en MoSCoW. Mis à jour à chaque PR —
sert de mémoire entre sessions de travail. Chaque case cochée = mergé sur
`main`.

## Must

- [x] Multi-comptes Google (switcher, un seul humain, plusieurs comptes liés)
      — `feat/multi-account-auth` (mergé, fixes inclus)
- [x] Scope OAuth étendu (`youtube` complet) + gestion playlists/favoris
      (créer une playlist, ajouter/retirer une vidéo, like/unlike)
      — `feat/playlist-management` (mergé)
- [x] Recherche (barre + page de résultats) — `feat/search` (mergé)
- [x] Page d'accueil : tendances + dernières vidéos des abonnements
      — `feat/home-feed` (mergé)
- [x] Refonte UI : navigation (sidebar/topbar), thème **glassmorphism dark**,
      cartes/menus, métadonnées vidéo (chaîne/date sous les vignettes et le
      lecteur), accueil personnalisable, restauration d'état à la navigation
      retour (scroll + `<KeepAlive>`) — `feat/ui-shell-redesign` (mergé).
      Revue UX incluse : badges de durée, progression de téléchargement
      réelle, tiroir de navigation mobile, mises à jour optimistes + toasts
      d'erreur/succès (favoris/playlists), icônes lucide, ordre des
      playlists personnalisable (état partagé Pinia), page "Vidéos aimées"
      dédiée + entrée de menu, endpoints regroupés sous `/api` (évite les
      collisions avec les routes du front), séparation dev/prod des
      services Docker Compose (`backend`/`backend-prod`, plus de port 8000
      exposé en profil prod).
- [x] Pages dédiées par section (Abonnements, Tendances, chaque Playlist)
      accessibles depuis le menu, avec un lien "Voir tout" + accueil moins
      chargé (aperçu limité par section) — `feat/section-pages` (mergé).
      Playlists/Favoris avaient déjà leur page dédiée (`/playlists/manage`,
      `/favorites`) — ajouté `/subscriptions` et `/trending`, entrées de
      sidebar, accueil limité à 6 vignettes/section.
- [x] Reprises en cours : position de lecture + statut vu/non vu par
      compte/vidéo, barre de progression sous les vignettes, menu "…" sous
      chaque vignette (marquer vu/non vu) — `feat/watch-progress` (mergé).
      Le lecteur reprend automatiquement à la position sauvegardée (si
      < 95% de la durée et pas marqué vu). Fix associé (branche séparée,
      commit fait après le merge de la PR) : `fix/video-durations` —
      `playlistItems.list`/`activities.list` n'exposent pas la durée de la
      vidéo (seulement celle de l'item), il manquait un appel groupé
      `videos.list(id=...)` pour l'afficher dans Playlists/Abonnements/
      Recherche (déjà correct pour Favoris/Tendances).
- [x] Pages chaîne (vidéos d'une chaîne, infos) + noms de chaîne cliquables
      partout (vignettes, lecteur) — `feat/channel-pages`. Passe par la
      playlist "uploads" de la chaîne (`channels.list(contentDetails)` +
      `playlistItems.list`, 1 unité) plutôt que `search.list` (100 unités)
      pour lister les vidéos, même logique que les abonnements. Ajout de
      `channel_id` à tous les payloads vidéo (résumé, items de playlist,
      recherche, abonnements) pour permettre le lien cliquable.
- [x] Tire-pour-rafraîchir sur mobile (pattern natif) en haut de l'accueil
      — `feat/pull-to-refresh`. Composant `PullToRefresh.vue` générique
      (gestes tactiles seulement, aucun effet sur desktop/souris), recharge
      abonnements/tendances/playlists/favoris + progression en parallèle.

## Should

- [x] Modale "Ajouter à une playlist" réutilisable partout (cartes vidéo,
      résultats de recherche, lecteur) — faite au fil des branches précédentes
- [x] Toasts de confirmation succès/erreur (ajout/retrait playlist, like, etc.)
      — `feat/ui-shell-redesign`
- [x] Skeletons de chargement + états vides soignés — `feat/loading-states`.
      `SkeletonCard.vue` (shimmer réutilisable via la classe globale
      `.skeleton`) remplace les "Chargement…" texte dans toutes les grilles
      de vidéos/playlists ; `EmptyState.vue` (icône + message) remplace les
      états vides plats, y compris ceux qui n'existaient pas encore
      (playlist vide, aucun favori/playlist sur l'accueil).

## Could

- [x] Tri/filtre des vidéos dans une playlist — `feat/playlist-sort-filter`.
      Filtre texte (titre/chaîne) + tri (ordre playlist, titre, date,
      durée), tout côté client (les items sont déjà chargés en entier).
- [x] Raccourcis clavier (lecteur, navigation) — `feat/keyboard-shortcuts`.
      Lecteur façon YouTube (espace/k lecture, flèches/j-l seek ±10s,
      flèches haut/bas volume, m mute, f plein écran). Navigation : "/"
      global vers la recherche avec focus auto. Tous ignorés si le focus
      est déjà dans un champ de saisie ou qu'une touche modificatrice est
      pressée.
- [x] Page "Historique" (`/history`, entrée de sidebar). L'API YouTube
      Data v3 n'expose pas l'historique de visionnage réel (confirmé :
      `activities.list` ne renvoie que l'activité de chaîne — uploads,
      likes — pas les vidéos regardées, même restriction que `WL`/`LL`
      ci-dessous) — fallback local via IndexedDB (`stores/history.js`,
      200 entrées max, dédoublonnées par vidéo, la plus récente en tête),
      journalisé à chaque ouverture du lecteur (`Player.vue`).

## Won't (pour l'instant)

- [ ] "Watch Later" natif et playlist "Liked videos" (`LL`) — bloqués côté
      API YouTube Data v3 (Google a coupé l'accès lecture/écriture aux
      playlists système `WL`/`LL` en 2016, mesure anti-abus, pas
      contournable sans scraper — hors scope du projet). "Favoris" dans
      l'app passe donc par `videos.rate`/`myRating=like`, resté supporté —
      pas gérable comme une playlist (pas dans "Gérer les playlists"),
      décision confirmée avec l'utilisateur.
- [ ] Commentaires
- [ ] Multi-utilisateurs (plusieurs humains distincts — seul le multi-comptes
      d'une même personne est prévu)
- [ ] Upload / gestion de chaîne

## Contraintes connues

- Quota YouTube Data API v3 : 10 000 unités/jour par défaut. `search.list`
  coûte 100 unités/appel (large pour un usage perso, à surveiller si usage
  intensif). `videos.list`/`activities.list`/`subscriptions.list` coûtent
  1 unité/appel.
- Pas d'API "accueil personnalisé" officielle — la page d'accueil est
  reconstruite à partir de tendances + abonnements, pas des recommandations
  YouTube réelles.
- Élargir un scope OAuth nécessite de l'ajouter explicitement dans Google
  Cloud Console → OAuth consent screen → Scopes, sinon Google le droppe
  silencieusement de la réponse du token (vécu avec `youtube.readonly`).
- Déploiement réel (quadlets + Traefik) : Traefik termine le TLS public puis
  parle en HTTP interne à Caddy. Sans `trusted_proxies` dans le Caddyfile,
  Caddy recalcule `X-Forwarded-Proto` depuis sa propre connexion (http) et
  l'envoie tel quel au backend malgré `--proxy-headers` côté uvicorn, ce qui
  faisait planter `/auth/callback` (`InsecureTransportError`, oauthlib voit
  un callback OAuth en http). Fixé via `trusted_proxies static private_ranges`
  dans `front/Caddyfile` (`fix/caddy-trusted-proxies`, mergé).
- Messages d'erreur yt-dlp différenciés — `feat/ytdlp-error-messages`.
  `downloader.py` renvoyait la trace brute de l'exception telle quelle.
  yt-dlp ne distingue la plupart des cas que par le texte du message (pas
  de sous-classe dédiée) sauf `GeoRestrictedError`/`UnavailableVideoError` ;
  reconnaissance des tournures les plus courantes (vidéo privée,
  vérification d'âge, réservée aux membres, supprimée, pas encore
  disponible) pour afficher un message actionnable côté lecteur au lieu
  du texte brut yt-dlp.

## Sécurité — revue et correctifs

- `fix/video-id-validation` : `video_id` n'était pas validé côté backend
  avant d'atterrir dans un chemin de fichier (`downloader.py`) et dans
  l'URL passée à yt-dlp. Contrainte ajoutée (`Path`/`Field` avec pattern
  `^[A-Za-z0-9_-]{11}$`, le format fixe d'un ID YouTube) sur toutes les
  routes concernées (`/video/*`, `/favorites/{video_id}`, `AddItemBody`).
  Le routing Starlette bloquait déjà les tentatives contenant un `/` (404,
  pas de correspondance de route), mais rien n'empêchait un ID mal formé
  sans slash d'atteindre `downloader.py` — corrigé.
- Vérifié à cette occasion : cookie de session `httponly`/`secure`/
  `samesite=lax`, flow OAuth avec PKCE + `state` correctement invalidé
  après usage (`getdel`), CORS restreint à `FRONTEND_ORIGIN` (pas de
  wildcard) — rien à signaler de ce côté.
- `SECRET_KEY` retiré de `config.py`/`.env.example` : résidu du squelette
  initial, jamais utilisé nulle part (les sessions sont des tokens
  aléatoires en Redis, pas des cookies signés) — un scanner de sécu sur un
  repo public l'aurait signalé comme "secret par défaut".
- Limite connue, pas corrigée : pas de rate-limiting sur
  `POST /video/{id}/prepare` (déclenche un téléchargement yt-dlp). Le
  garde-fou existant (`prepare_video` ignore un appel si déjà en cours
  pour le même `video_id`) limite les doublons mais pas le nombre total de
  téléchargements concurrents déclenchables par un compte authentifié.
  Acceptable pour un usage perso mono-utilisateur ; à revisiter si le
  projet évolue vers un vrai multi-utilisateurs.

## Tests & CI

- `feat/tests-ci` : premiers tests automatisés + CI GitHub Actions
  (`.github/workflows/ci.yml`, deux jobs indépendants backend/frontend).
  - Backend (`pytest`, `server/tests/`) : fonctions pures de
    `downloader.py`, et vérification que les routes protégées répondent
    bien 401 sans session (pas besoin de Redis pour ces cas — ils
    échouent avant tout accès au cache).
  - Frontend (`vitest`, `front/src/utils/format.test.js`) : les
    fonctions pures de formatage (`formatDuration`, `formatViewCount`,
    `formatRelativeDate`).
  - Volontairement pas encore de tests composants Vue (pas
    d'`@vue/test-utils` en place) ni de tests touchant l'API YouTube
    réelle (nécessiterait des credentials Google en CI) — à évaluer si
    le projet grossit encore.

## Dépôt public

- `docs/public-repo-prep` : préparation du passage du dépôt en public —
  licence MIT (`LICENSE`), README refondu (avertissement légal, schémas
  d'architecture et de séquence en Mermaid, tableau des dépendances +
  crédits/licences), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor
  Covenant 2.1), `SECURITY.md`, templates d'issues et de PR GitHub.
  `CLAUDE.md` mis à jour en conséquence (le code est public, l'usage reste
  personnel par instance).
