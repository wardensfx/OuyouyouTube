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
- [ ] Refonte UI : navigation (sidebar/topbar), thème **glassmorphism dark**,
      cartes/menus, métadonnées vidéo (chaîne/date sous les vignettes et le
      lecteur), accueil personnalisable, restauration d'état à la navigation
      retour (scroll + `<KeepAlive>`) — `feat/ui-shell-redesign` (PR ouverte,
      pas encore mergée). Revue UX incluse : badges de durée, progression de
      téléchargement réelle, tiroir de navigation mobile, mises à jour
      optimistes + toasts d'erreur (favoris/playlists), icônes lucide.
- [ ] Pages dédiées par section (Abonnements, Tendances, chaque Playlist)
      accessibles depuis le menu, avec un lien "Voir tout" + accueil moins
      chargé (aperçu limité par section) — `feat/section-pages`
- [ ] Reprises en cours : position de lecture + statut vu/non vu par
      compte/vidéo, barre de progression sous les vignettes, menu "…" sous
      chaque vignette (marquer vu/non vu) — `feat/watch-progress`
- [ ] Pages chaîne (vidéos d'une chaîne, infos) + noms de chaîne cliquables
      partout (vignettes, lecteur) — `feat/channel-pages`
- [ ] Tire-pour-rafraîchir sur mobile (pattern natif) en haut de l'accueil
      — `feat/pull-to-refresh`

## Should

- [x] Modale "Ajouter à une playlist" réutilisable partout (cartes vidéo,
      résultats de recherche, lecteur) — faite au fil des branches précédentes
- [x] Toasts de confirmation d'erreur (ajout/retrait playlist, like, etc.)
      — `feat/ui-shell-redesign`
- [ ] Skeletons de chargement + états vides soignés

## Could

- [ ] Tri/filtre des vidéos dans une playlist
- [ ] Raccourcis clavier (lecteur, navigation)

## Won't (pour l'instant)

- [ ] "Watch Later" natif — bloqué côté API YouTube Data v3 (Google a coupé
      l'accès lecture/écriture à la playlist système `WL` en 2016, mesure
      anti-abus, pas contournable sans scraper — hors scope du projet).
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
