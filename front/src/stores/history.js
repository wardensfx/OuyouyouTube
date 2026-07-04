import { defineStore } from 'pinia'
import { getValue, setValue } from '../db'

// L'API YouTube Data v3 n'expose pas l'historique de visionnage réel de
// l'utilisateur (activities.list ne renvoie que l'activité de chaîne —
// uploads, likes... — pas les vidéos regardées), même restriction que les
// playlists système WL/LL déjà documentée dans ROADMAP.md. Fallback local :
// chaque vidéo ouverte est journalisée ici. Champs à plat, shape stable,
// pour pouvoir être mirroré tel quel vers un futur endpoint /api/history.
const STORE = 'history'
const KEY = 'entries'
const MAX_ENTRIES = 200

export const useHistoryStore = defineStore('history', {
  state: () => ({ entries: [], _loaded: null }),
  actions: {
    load() {
      if (!this._loaded) {
        this._loaded = getValue(STORE, KEY).then((stored) => {
          this.entries = Array.isArray(stored) ? stored : []
        })
      }
      return this._loaded
    },
    async record(video) {
      await this.load()
      const entry = {
        video_id: video.video_id,
        title: video.title,
        channel: video.channel,
        channel_id: video.channel_id,
        thumbnail: video.thumbnail,
        duration: video.duration,
        watched_at: new Date().toISOString(),
      }
      const rest = this.entries.filter((e) => e.video_id !== video.video_id)
      const next = [entry, ...rest].slice(0, MAX_ENTRIES)
      this.entries = next
      return setValue(STORE, KEY, next)
    },
  },
})
