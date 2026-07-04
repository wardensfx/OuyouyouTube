<script setup>
import { Inbox } from '@lucide/vue'

defineProps({
  message: { type: String, required: true },
  icon: { type: [Object, Function], default: () => Inbox },
})
</script>

<template>
  <div class="empty-state">
    <component :is="icon" :size="32" class="empty-state__icon" />
    <p class="empty-state__message">{{ message }}</p>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2.5rem 1rem;
  color: var(--text-dim);
  text-align: center;
}
.empty-state__icon {
  opacity: 0.5;
}
.empty-state__message {
  margin: 0;
  font-size: 0.9rem;
}
</style>
