<script setup>
defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: null },
})
defineEmits(['retry'])
</script>

<template>
  <div v-if="loading" class="loadmore">
    <span class="loadmore__spinner" />
  </div>
  <div v-else-if="error" class="loadmore loadmore--error">
    <span>{{ error }}</span>
    <button class="loadmore__retry" @click="$emit('retry')">Réessayer</button>
  </div>
</template>

<style scoped>
.loadmore {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0;
  font-size: 0.85rem;
  opacity: 0.8;
}
.loadmore--error {
  color: var(--danger);
  flex-direction: column;
}
.loadmore__spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: loadmore-spin 0.8s linear infinite;
}
@keyframes loadmore-spin {
  to {
    transform: rotate(360deg);
  }
}
.loadmore__retry {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-pill);
  color: inherit;
  padding: 0.4rem 0.9rem;
  font-size: 0.85rem;
  cursor: pointer;
}
</style>
