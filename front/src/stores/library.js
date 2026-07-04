import { defineStore } from 'pinia'
import { api } from '../api/client'
import { useToastStore } from './toast'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    playlists: [],
    favorites: [],
    loading: false,
    error: null,
  }),
  actions: {
    async loadAll() {
      this.loading = true
      this.error = null
      try {
        const [playlists, favorites] = await Promise.all([
          api.getPlaylists(),
          api.getFavorites(),
        ])
        this.playlists = playlists
        this.favorites = favorites
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    async createPlaylist(title) {
      try {
        const created = await api.createPlaylist(title)
        this.playlists = [...this.playlists, created]
        return created
      } catch (e) {
        useToastStore().push(`Impossible de créer la playlist : ${e.message}`)
        throw e
      }
    },

    // Mise à jour optimiste (item_count) : on ne sait pas forcément dans
    // quelle playlist regarder les items, donc pas d'ajout local à une
    // liste d'items ici — juste le compteur affiché sur PlaylistCard.
    async addToPlaylist(playlistId, video) {
      const playlist = this.playlists.find((p) => p.id === playlistId)
      if (playlist) playlist.item_count += 1
      try {
        await api.addPlaylistItem(playlistId, video.video_id)
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
      } catch (e) {
        this.favorites = prev
        useToastStore().push(`Échec du retrait des favoris : ${e.message}`)
        throw e
      }
    },
  },
})
