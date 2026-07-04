import { defineStore } from 'pinia'
import { getValue, setValue } from '../db'

// YouTube Data API ne propose pas d'ordre personnalisé pour "mes playlists"
// — c'est donc une préférence locale. État partagé (Pinia) plutôt qu'un ref
// par composant : sinon un changement fait depuis une page (ex. Gérer les
// playlists) ne se reflète pas ailleurs (ex. la sidebar) tant que ce
// composant-là n'est pas remonté.
const STORE = 'playlist_order'
const KEY = 'ids'

export const usePlaylistOrderStore = defineStore('playlistOrder', {
  state: () => ({ ids: [], _loaded: null }),
  actions: {
    // Mémoïsé : le premier appel déclenche la lecture IndexedDB, les
    // suivants attendent la même promesse sans relire.
    _ensureLoaded() {
      if (!this._loaded) {
        this._loaded = getValue(STORE, KEY).then((stored) => {
          this.ids = Array.isArray(stored) ? stored : []
        })
      }
      return this._loaded
    },
    async sync(playlists) {
      await this._ensureLoaded()
      const known = this.ids.filter((id) => playlists.some((p) => p.id === id))
      const extra = playlists.filter((p) => !this.ids.includes(p.id)).map((p) => p.id)
      const next = [...known, ...extra]
      const changed = next.length !== this.ids.length || next.some((id, i) => id !== this.ids[i])
      if (changed) this.ids = next
    },
    async move(id, dir) {
      await this._ensureLoaded()
      const arr = [...this.ids]
      const idx = arr.indexOf(id)
      const target = idx + dir
      if (idx === -1 || target < 0 || target >= arr.length) return
      ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
      this.ids = arr
      // Persist the plain array, not `this.ids` — once assigned to state,
      // Pinia wraps it in a reactive Proxy that IndexedDB's structured
      // clone algorithm can't serialize.
      return setValue(STORE, KEY, arr)
    },
  },
})
