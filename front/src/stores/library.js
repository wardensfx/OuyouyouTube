import { defineStore } from 'pinia'
import { api } from '../api/client'

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
      await api.createPlaylist(title)
      await this.loadAll()
    },

    async addToPlaylist(playlistId, videoId) {
      await api.addPlaylistItem(playlistId, videoId)
      await this.loadAll()
    },

    async likeVideo(videoId) {
      await api.likeVideo(videoId)
      await this.loadAll()
    },

    async unlikeVideo(videoId) {
      await api.unlikeVideo(videoId)
      await this.loadAll()
    },
  },
})
