import { defineStore } from 'pinia'
import { api } from '../api/client'
import { useToastStore } from './toast'

export const useProgressStore = defineStore('progress', {
  state: () => ({ items: {} }),
  actions: {
    // Un seul appel groupé par grille chargée, plutôt qu'un appel par
    // vignette — évite le N+1 sur les pages qui listent des vidéos.
    async fetchFor(videoIds) {
      const ids = [...new Set(videoIds)].filter(Boolean)
      if (!ids.length) return
      try {
        const result = await api.getProgressBulk(ids)
        this.items = { ...this.items, ...result }
      } catch {
        // Non bloquant : au pire la barre de progression ne s'affiche pas.
      }
    },

    async reportProgress(videoId, position, duration) {
      this.items = { ...this.items, [videoId]: { position, duration, watched: this.items[videoId]?.watched } }
      try {
        await api.saveProgress(videoId, position, duration)
      } catch {
        // Non bloquant : un rapport de progression raté n'a pas besoin d'un toast.
      }
    },

    async setWatched(videoId, watched) {
      const prev = this.items[videoId]
      this.items = { ...this.items, [videoId]: { position: prev?.position ?? 0, duration: prev?.duration ?? 0, watched } }
      try {
        await api.setWatched(videoId, watched)
      } catch (e) {
        this.items = { ...this.items, [videoId]: prev }
        useToastStore().push(`Échec : ${e.message}`)
      }
    },
  },
})
