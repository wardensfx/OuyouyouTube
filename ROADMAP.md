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
- [x] Notes de version consultables depuis l'app — clic sur le numéro de
      version (bas de la sidebar) ouvre une modale qui va chercher
      `CHANGELOG.md` sur GitHub, au tag exact de la version en cours
      d'exécution (`v{version}`, posé par `release-please`), plutôt qu'à la
      branche `main` — évite un décalage si l'instance déployée n'a pas
      encore été mise à jour. Récupéré à l'exécution plutôt qu'à la
      compilation : `CHANGELOG.md` vit à la racine du dépôt, hors du
      contexte de build Docker du front (`front/` seulement, cf.
      `front/Dockerfile` + `docker-compose.yml`/`publish-images.yml`), donc
      un lien symbolique/`readFileSync` à la compilation aurait cassé
      silencieusement l'image de prod. `marked` (import dynamique, hors du
      bundle principal) rend le markdown ; repli "Voir sur GitHub" si le
      fetch échoue. Modale sur le même patron d'accessibilité que
      `AddToPlaylistModal.vue` (`role="dialog"`, piège de focus, Escape).

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
- Batch de correctifs recette — `claude/open-issues-q1blka` (issues #74-78,
  auraient dû être traitées en PR séparées, batchées par erreur) :
  - #77 : grille 2 colonnes déséquilibrée par un titre contenant un token
    non-sécable (URL/hashtag) — `min-width: 0` manquant sur `.card`
    (`VideoCard.vue`), l'item de grille gardait son min-content en largeur
    minimale.
  - #76 : `overscroll-behavior-y: contain` (fix #67) insuffisant sur iOS
    Safari, le rubber-band natif restait visible — `PullToRefresh.vue`
    appelle maintenant `preventDefault()` sur le geste de tiré (uniquement
    en haut de page, jamais pendant un scroll normal).
  - #75 : mise à jour PWA jamais détectée sur iOS (l'app installée est
    suspendue puis reprise par WKWebView, `main.js` ne se ré-exécute pas) —
    écoute de `pageshow`/`event.persisted` pour forcer un
    `registration.update()` au retour au premier plan.
  - #74 : artwork MediaSession (320×180) potentiellement au-dessus de la
    limite ~128×128 rapportée sur iOS — ajout de `thumbnail_small`
    (120×90, thumbnail "default" de l'API) dans `_video_summary`, listée
    en premier dans `MediaMetadata.artwork`.
  - #78 (pagination) : traité partiellement dans cette même branche —
    pagination réelle (`page_token` + cache Redis par page, au lieu
    d'accumuler toutes les pages via `list_next`) et scroll infini
    (`useInfiniteScroll.js`, `IntersectionObserver`) pour Favoris,
    Tendances, Vidéos de chaîne et Recherche.
- Suite #78 (playlist items) — `claude/open-issues-q1blka`, PR séparée
  après le merge du batch ci-dessus. `PlaylistDetail.vue` a aussi son tri
  (titre/date/durée) et son filtre plein-ensemble côté client : paginer
  `get_playlist_items` sans plus casserait un tri qui se réordonnerait
  sous les yeux de l'utilisateur à chaque page chargée. Solution : scroll
  infini seulement en mode "Ordre de la playlist" + filtre vide ; dès que
  l'utilisateur choisit un autre tri ou tape un filtre, chargement
  automatique de toutes les pages restantes une bonne fois pour toutes
  (`ensureFullyLoaded()`), le tri/filtre redevient ensuite instantané côté
  client. Liste des playlists elle-même (`get_my_playlists`) volontairement
  laissée non paginée : alimente le réordonnancement drag-and-drop
  (`ManagePlaylists.vue`) et le picker (`AddToPlaylistModal.vue`), et le
  nombre de playlists d'un compte perso reste d'un tout autre ordre de
  grandeur que l'historique d'une chaîne.

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
- `front/src/db/` (IndexedDB — playlist order, historique) n'était pas
  scopé par compte : IndexedDB n'est cloisonné que par origine, pas par
  compte Google actif côté session, contrairement à tout l'état
  équivalent côté serveur (favoris, playlists, vu/non-vu). Un utilisateur
  avec plusieurs comptes liés (switcher) voyait l'historique/l'ordre des
  playlists d'un compte se mélanger avec ceux d'un autre sur le même
  appareil. Corrigé : la base est maintenant nommée
  `ouyouyoutube:{account_id}` (résolu via `/api/auth/accounts`), une
  bascule de compte recharge de toute façon la page entière donc pas
  besoin de gérer un changement de compte "à chaud". Trouvé lors d'une
  revue de sécurité automatisée sur les changements de la session
  précédente (issue #56).
- Revue multi-agents (sécu/archi/UI-UX) sur les changements de pagination
  de la session précédente (issues #82-#99, `claude/*` puis PR par PR,
  toutes mergées) :
  - #82 (critique) : `get_playlist_items`/`get_video_details` (cache Redis)
    n'étaient pas namespacés par `account_id`, contrairement aux autres
    caches — un compte lié voyait une playlist/vidéo privée d'un autre
    compte lié à la même session si mise en cache dans la fenêtre de TTL
    (15 min), sans repasser par la vérification de permission Google.
  - #83 : retirer un compte lié ne purgeait/révoquait pas son jeton OAuth
    (`unlink_account`), restait valide en Redis jusqu'à 30 jours après.
    Révoque désormais côté Google + supprime l'enregistrement Redis, sauf
    si un autre appareil/session a encore ce compte lié (vérifié par scan
    des sessions avant de couper).
  - #85 : `docker-compose.yml` publiait le port Redis (`6379:6379`) sans
    authentification sur toutes les interfaces de l'hôte — restreint à
    `127.0.0.1`. Ne concernait que le chemin docker-compose, pas les
    quadlets Podman (déjà correctement confinés au réseau interne).
  - #86 : `playlist_id`/`item_id` non validés pouvaient élargir le motif
    glob de `delete_prefix` (SCAN Redis) et invalider le cache d'une autre
    playlist — pattern de charset borné ajouté, même principe que
    `video_id`.
  - #84 (décision produit) : pas de liste blanche de comptes Google
    autorisés à s'authentifier par défaut (l'instance est sensée être
    protégée en amont — proxy d'auth si exposée) ; `ALLOWED_GOOGLE_EMAILS`
    optionnel ajouté dans `config.py`/`.env.example` pour qui veut quand
    même la restriction, no-op si non défini.
  - #87 : le bouton "J'aime" se basait sur `library.favorites` (liste
    partielle depuis la pagination des favoris, #78) pour savoir si une
    vidéo était aimée — faux pour toute vidéo hors des pages déjà
    chargées. `get_video_details` renvoie maintenant un champ `liked`
    autoritaire (`videos.getRating`, 1 unité de quota) pour la vidéo en
    cours dans le lecteur.
  - #88/#89 : `loadMore()` avalait ses erreurs silencieusement (aucune
    dans les 5 vues paginées, contrairement à `load()`) et dupliquait la
    même logique de chargement/état partout — composable
    `usePaginatedList` + composant `LoadMoreStatus.vue` partagés ;
    `api/client.js` mappe désormais les erreurs HTTP vers un message
    français plutôt que la ligne de statut brute.
  - #90 : ajout de `fakeredis`/`pytest-asyncio` (dev only) et de tests
    unitaires vérifiant que chaque mutation (like, ajout/retrait d'item,
    suppression de playlist) invalide bien toutes les pages en cache
    concernées, pas une clé fixe qui n'existe plus sous cette forme.
  - #91/#92/#93 (accessibilité) : `useEscapeToClose.js` partagé par les
    modales/menus (Échap + focus rendu au déclencheur) ; restructuration
    de `VideoCard.vue` pour ne plus imbriquer de boutons dans le
    `RouterLink` (HTML invalide) ; agrandissement des zones tactiles des
    petits boutons icône via un `::before` en `position: absolute`
    (n'agrandit pas le rendu visuel).
  - #94/#95/#96/#97/#99 (UI, plus mineur) : `min-width: 0` manquant sur
    `PlaylistCard.vue` (même bug que #77) ; retour visuel figé/estompé
    pendant le chargement complet d'un tri dans `PlaylistDetail.vue` ;
    `--accent-strong` (déjà déclarée, jamais utilisée) redéfinie plus
    sombre pour les boutons à texte blanc (contraste WCAG AA) ;
    `Channel.vue`/`History.vue` alignées sur le patron skeleton/empty-state
    standard ; petits correctifs CSS (arrondi du pourcentage de
    téléchargement, `overflow-wrap` sur les titres, `min-width: 0` sur
    `AccountSwitcher.vue`).
  - #98 : terminologie unifiée sur "Vidéos aimées" (section d'accueil,
    toasts, tooltip du cœur) — cohérent avec la sidebar et la page dédiée,
    qui l'utilisaient déjà. Le bouton du lecteur garde "J'aime"/"Aimée"
    (verbe d'action sur un bouton, pas un nom de fonctionnalité).

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
