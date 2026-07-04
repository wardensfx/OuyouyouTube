import { defineStore } from 'pinia'

// YouTube Data API ne propose pas d'ordre personnalisé pour "mes playlists"
// — c'est donc une préférence locale. État partagé (Pinia) plutôt qu'un ref
// par composant : sinon un changement fait depuis une page (ex. Gérer les
// playlists) ne se reflète pas ailleurs (ex. la sidebar) tant que ce
// composant-là n'est pas remonté — localStorage seul n'est pas réactif.
const KEY = 'playlist_order_v1'

function load() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY))
    return Array.isArray(raw) ? raw : []
  } catch {
    return []
  }
}

export const usePlaylistOrderStore = defineStore('playlistOrder', {
  state: () => ({ ids: load() }),
  actions: {
    sync(playlists) {
      const known = this.ids.filter((id) => playlists.some((p) => p.id === id))
      const extra = playlists.filter((p) => !this.ids.includes(p.id)).map((p) => p.id)
      const next = [...known, ...extra]
      const changed = next.length !== this.ids.length || next.some((id, i) => id !== this.ids[i])
      if (changed) this.ids = next
    },
    move(id, dir) {
      const arr = [...this.ids]
      const idx = arr.indexOf(id)
      const target = idx + dir
      if (idx === -1 || target < 0 || target >= arr.length) return
      ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
      this.ids = arr
      localStorage.setItem(KEY, JSON.stringify(this.ids))
    },
  },
})
