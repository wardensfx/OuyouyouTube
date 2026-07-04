# Roadmap

Suivi des fonctionnalités du clone, en MoSCoW. Mis à jour à chaque PR —
sert de mémoire entre sessions de travail. Chaque case cochée = mergé sur
`main`.

## Must

- [x] Multi-comptes Google (switcher, un seul humain, plusieurs comptes liés)
      — `feat/multi-account-auth` (mergé sur `main` ; 2 commits de fix
      poussés après coup — scope OAuth, logout/avatar — encore en PR à part,
      pas encore mergés)
- [ ] Scope OAuth étendu (`youtube` complet) + gestion playlists/favoris
      (créer une playlist, ajouter/retirer une vidéo, like/unlike)
      — `feat/playlist-management` (PR ouverte, pas encore mergée)
- [ ] Recherche (barre + page de résultats) — `feat/search`
- [ ] Page d'accueil : tendances + dernières vidéos des abonnements
      — `feat/home-feed`
- [ ] Refonte UI : navigation (sidebar/topbar), thème **glassmorphism dark**
      (demande explicite : look moderne, verre dépoli/flou, sombre),
      cartes/menus — `feat/ui-shell-redesign`

## Should

- [ ] Reprises en cours ("continue watching" — tracking de la position de
      lecture par compte/vidéo, section dédiée sur l'accueil)
- [ ] Accueil personnalisable (choix/ordre des sections)
- [ ] Modale "Ajouter à une playlist" réutilisable partout (cartes vidéo,
      résultats de recherche, lecteur)
- [ ] Skeletons de chargement + états vides soignés
- [ ] Toasts de confirmation (ajout/retrait playlist, like, etc.)

## Could

- [ ] Pages chaîne (vidéos d'une chaîne, infos)
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
