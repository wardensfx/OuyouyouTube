import { defineStore } from 'pinia'
import { api } from '../api/client'
import { useToastStore } from './toast'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    playlists: [],
    favorites: [],
    favoritesNextPageToken: null,
    favoritesLoadingMore: false,
    // Séparée de `error` (chargement initial) : un échec de page suivante ne
    // doit pas remplacer toute la grille des favoris déjà affichée par un
    // état d'erreur plein écran.
    favoritesLoadMoreError: null,
    loading: false,
    error: null,
  }),
  actions: {
    async loadAll() {
      this.loading = true
      this.error = null
      try {
        const [playlists, favoritesPage] = await Promise.all([
          api.getPlaylists(),
          api.getFavorites(),
        ])
        this.playlists = playlists
        this.favorites = favoritesPage.items
        this.favoritesNextPageToken = favoritesPage.next_page_token
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    // Favoris potentiellement non bornés (cf. issue #78) : une page à la
    // fois derrière un scroll infini (voir Liked.vue) plutôt que tout
    // charger en un appel.
    async loadMoreFavorites() {
      if (!this.favoritesNextPageToken || this.favoritesLoadingMore) return
      this.favoritesLoadingMore = true
      this.favoritesLoadMoreError = null
      try {
        const page = await api.getFavorites(this.favoritesNextPageToken)
        this.favorites = [...this.favorites, ...page.items]
        this.favoritesNextPageToken = page.next_page_token
        return page.items
      } catch (e) {
        this.favoritesLoadMoreError = e.message
        return []
      } finally {
        this.favoritesLoadingMore = false
      }
    },

    async createPlaylist(title) {
      try {
        const created = await api.createPlaylist(title)
        this.playlists = [...this.playlists, created]
        useToastStore().push(`Playlist « ${title} » créée`, 'success')
        return created
      } catch (e) {
        useToastStore().push(`Impossible de créer la playlist : ${e.message}`)
        throw e
      }
    },

    async renamePlaylist(playlistId, title) {
      const playlist = this.playlists.find((p) => p.id === playlistId)
      const prevTitle = playlist?.title
      if (playlist) playlist.title = title
      try {
        await api.renamePlaylist(playlistId, title)
        useToastStore().push('Playlist renommée', 'success')
      } catch (e) {
        if (playlist) playlist.title = prevTitle
        useToastStore().push(`Échec du renommage : ${e.message}`)
        throw e
      }
    },

    async deletePlaylist(playlistId) {
      const prev = this.playlists
      this.playlists = this.playlists.filter((p) => p.id !== playlistId)
      try {
        await api.deletePlaylist(playlistId)
        useToastStore().push('Playlist supprimée', 'success')
      } catch (e) {
        this.playlists = prev
        useToastStore().push(`Échec de la suppression : ${e.message}`)
        throw e
      }
    },

    // Mise à jour optimiste (item_count) : on ne sait pas forcément dans
    // quelle playlist regarder les items, donc pas d'ajout local à une
    // liste d'items ici — juste le compteur affiché sur PlaylistCard (la
    // page de la playlist elle-même se rafraîchit toute seule via
    // onActivated dans PlaylistDetail.vue).
    async addToPlaylist(playlistId, video) {
      const playlist = this.playlists.find((p) => p.id === playlistId)
      if (playlist) playlist.item_count += 1
      try {
        await api.addPlaylistItem(playlistId, video.video_id)
        useToastStore().push(
          playlist ? `Ajoutée à « ${playlist.title} »` : 'Ajoutée à la playlist',
          'success',
        )
      } catch (e) {
        if (playlist) playlist.item_count -= 1
        useToastStore().push(`Échec de l'ajout à la playlist : ${e.message}`)
        throw e
      }
    },

    async likeVideo(video) {
      const already = this.favorites.some((v) => v.video_id === video.video_id)
      if (!already) this.favorites = [video, ...this.favorites]
      try {
        await api.likeVideo(video.video_id)
        useToastStore().push('Ajoutée aux favoris', 'success')
      } catch (e) {
        if (!already) this.favorites = this.favorites.filter((v) => v.video_id !== video.video_id)
        useToastStore().push(`Échec de l'ajout aux favoris : ${e.message}`)
        throw e
      }
    },

    async unlikeVideo(videoId) {
      const prev = this.favorites
      this.favorites = this.favorites.filter((v) => v.video_id !== videoId)
      try {
        await api.unlikeVideo(videoId)
        useToastStore().push('Retirée des favoris', 'success')
      } catch (e) {
        this.favorites = prev
        useToastStore().push(`Échec du retrait des favoris : ${e.message}`)
        throw e
      }
    },
  },
})
