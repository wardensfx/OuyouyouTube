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
  },
})
