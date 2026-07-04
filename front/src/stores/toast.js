import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({ items: [] }),
  actions: {
    push(message, type = 'error') {
      const id = `${Date.now()}-${Math.random()}`
      this.items.push({ id, message, type })
      setTimeout(() => this.dismiss(id), 4000)
    },
    dismiss(id) {
      this.items = this.items.filter((t) => t.id !== id)
    },
  },
})
